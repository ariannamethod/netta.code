/* Netta's pipe/framebuffer platform for unmodified Doom Generic engine sources.
 * GPL-2.0-or-later, like the engine. No window, sound, joystick, or network API.
 */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include <math.h>
#include "doomgeneric.h"
#include "doomkeys.h"
#include "doomstat.h"
#include "d_loop.h"
#include "d_items.h"
#include "p_local.h"
#include "r_main.h"
#include "m_random.h"

static unsigned short events[64];
static unsigned read_event, write_event, frames;
static const unsigned char keys[] = {KEY_LEFTARROW, KEY_RIGHTARROW, KEY_UPARROW,
                                     KEY_STRAFE_L, KEY_STRAFE_R, KEY_FIRE};
static const char *names[] = {"turn_left", "turn_right", "move_forward",
                             "strafe_left", "strafe_right", "shoot"};

void DG_Init(void) {}
void DG_DrawFrame(void) { ++frames; }
void DG_SetWindowTitle(const char *title) { fprintf(stderr, "Doom title: %s\n", title); }
void DG_SleepMs(uint32_t ms) {
    struct timespec delay = {ms / 1000, (ms % 1000) * 1000000};
    nanosleep(&delay, NULL);
}
uint32_t DG_GetTicksMs(void) {
    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);
    return (uint32_t)(now.tv_sec * 1000 + now.tv_nsec / 1000000);
}
int DG_GetKey(int *pressed, unsigned char *key) {
    if (read_event == write_event) return 0;
    unsigned short event = events[(read_event++) % 64];
    *pressed = event >> 8;
    *key = event & 255;
    return 1;
}
static void action(int selected) {
    static int previous = -1;
    if (previous == selected) return;
    if (previous >= 0) events[(write_event++) % 64] = keys[previous];
    events[(write_event++) % 64] = 256 | keys[selected];
    previous = selected;
}
static void frame(const char *path) {
    FILE *output = fopen(path, "wb");
    if (!output) { perror(path); exit(2); }
    fprintf(output, "P6\n%d %d\n255\n", DOOMGENERIC_RESX, DOOMGENERIC_RESY);
    for (unsigned i = 0; i < DOOMGENERIC_RESX * DOOMGENERIC_RESY; ++i) {
        uint32_t pixel = DG_ScreenBuffer[i];
        unsigned char rgb[] = {pixel >> 16, pixel >> 8, pixel};
        fwrite(rgb, 1, 3, output);
    }
    fclose(output);
}
static void state(void) {
    player_t *player = &players[consoleplayer];
    mobj_t *body = player->mo;
    mobj_t *focus = NULL;
    double largest = -1, direction = 0;
    if (gamestate == GS_LEVEL && body && player->health > 0) {
        for (thinker_t *cursor = thinkercap.next; cursor != &thinkercap; cursor = cursor->next) {
            if (cursor->function.acp1 != (actionf_p1)P_MobjThinker) continue;
            mobj_t *object = (mobj_t *)cursor;
            if (object == body || object->health <= 0 || !(object->flags & MF_COUNTKILL)) continue;
            angle_t angle = R_PointToAngle2(body->x, body->y, object->x, object->y);
            double delta = (int32_t)(angle - body->angle) * (360.0 / 4294967296.0);
            if (fabs(delta) > 45 || !P_CheckSight(body, object)) continue;
            double dx = (double)object->x - body->x, dy = (double)object->y - body->y;
            double size = object->radius / fmax(1.0, hypot(dx, dy));
            if (size > largest) { largest = size; direction = delta; focus = object; }
        }
    }
    const char *scene = focus == NULL ? "empty" : direction > 15 ? "left" : direction < -15 ? "right" : "center";
    ammotype_t kind = weaponinfo[player->readyweapon].ammo;
    int ammunition = kind == am_noammo ? 0 : player->ammo[kind];
    printf("NETTA {\"tic\":%d,\"frames\":%u,\"terminal\":%s,\"dead\":%s,"
           "\"gamestate\":%d,\"variables\":{\"health\":%d,\"ammo\":%d,\"weapon\":%d,\"kills\":%d,"
           "\"x\":%.6f,\"y\":%.6f,\"angle\":%.6f,\"ammo_inventory\":[%d,%d,%d,%d]},"
           "\"observation\":{\"health\":%d,\"ammo\":%d,\"scene\":\"%s\"},\"focus\":",
           gametic, frames, gamestate != GS_LEVEL || player->health <= 0 ? "true" : "false",
           player->health <= 0 ? "true" : "false", gamestate, player->health, ammunition,
           player->readyweapon, player->killcount,
           body ? body->x / 65536.0 : 0, body ? body->y / 65536.0 : 0,
           body ? body->angle * (360.0 / 4294967296.0) : 0,
           player->ammo[0], player->ammo[1], player->ammo[2], player->ammo[3],
           player->health <= 25 ? 25 : player->health <= 75 ? 60 : 100,
           ammunition > 0 ? 10 : 0, scene);
    if (focus) printf("{\"type\":%d,\"health\":%d,\"angle_delta\":%.6f,\"relative_size\":%.6f}",
                      focus->type, focus->health, direction, largest);
    else printf("null");
    printf("}\n");
    fflush(stdout);
}
int main(int argc, char **argv) {
    unsigned seed = 0;
    for (int i = 1; i + 1 < argc; ++i)
        if (!strcmp(argv[i], "-netta-seed")) seed = (unsigned)strtoul(argv[i + 1], NULL, 10);
    singletics = true;
    doomgeneric_Create(argc, argv);
    /* Vanilla Doom uses a 256-entry gameplay RNG table. All map initialization
       is unchanged; this selects the deterministic post-load RNG phase. */
    for (unsigned i = 0; i < seed % 256; ++i) P_Random();
    state();
    char line[256], command[32], argument[128], trailing[2];
    int ticks;
    while (fgets(line, sizeof(line), stdin)) {
        if (!strcmp(line, "quit\n")) return 0;
        if (sscanf(line, "%31s %127s %d %1s", command, argument, &ticks, trailing) == 3 && !strcmp(command, "step")) {
            int selected = -1;
            for (int i = 0; i < 6; ++i) if (!strcmp(argument, names[i])) selected = i;
            if (selected < 0 || ticks < 1 || ticks > 16) return 2;
            action(selected);
            for (int i = 0; i < ticks && gamestate == GS_LEVEL && players[consoleplayer].health > 0; ++i)
                doomgeneric_Tick();
            state();
        } else if (sscanf(line, "%31s %127s %1s", command, argument, trailing) == 2 && !strcmp(command, "frame")) {
            if (strspn(argument, "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-") != strlen(argument)
                || argument[0] == '.') return 2;
            frame(argument);
            printf("NETTA {\"frame\":\"%s\",\"width\":%d,\"height\":%d}\n", argument, DOOMGENERIC_RESX, DOOMGENERIC_RESY);
            fflush(stdout);
        } else return 2;
    }
    return 0;
}
