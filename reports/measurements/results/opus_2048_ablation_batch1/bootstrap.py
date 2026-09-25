import json, random, statistics
BDIR="/private/tmp/claude-501/-Users-ataeff/b9aee79d-3176-4319-b2ca-9773fa083907/scratchpad/batch1"
random.seed(20260925)

def load(arm):
    m={}
    for line in open(f"{BDIR}/{arm}_eval/trained.jsonl"):
        d=json.loads(line)
        m[d["episode_seed"]]=d.get("reward",0.0)
    return m

arms={a:load(a) for a in ("count","full","head_off","credit_off","support_off")}
full=arms["full"]

def paired_ci(a,b,n=10000):
    keys=sorted(set(a)&set(b))
    diffs=[a[k]-b[k] for k in keys]
    mean=statistics.fmean(diffs)
    boots=[]
    for _ in range(n):
        s=[diffs[random.randrange(len(diffs))] for _ in diffs]
        boots.append(statistics.fmean(s))
    boots.sort()
    lo=boots[int(.025*n)]; hi=boots[int(.975*n)]
    return len(keys),mean,lo,hi

print("paired reward diff (full - arm), 95%% bootstrap CI over shared episode seeds")
print("%-22s %5s %9s %20s"%("comparison","n","mean","95% CI"))
for arm in ("count","head_off","credit_off","support_off"):
    n,mean,lo,hi=paired_ci(full,arms[arm])
    crosses = lo<=0<=hi
    verdict = "CROSSES 0" if crosses else ("full>arm" if mean>0 else "full<arm")
    print("full - %-15s %5d %9.5f   [%8.5f, %8.5f]  %s"%(arm,n,mean,lo,hi,verdict))
# organ-pays reading: full - leave_one_out > 0 means that organ carries weight
