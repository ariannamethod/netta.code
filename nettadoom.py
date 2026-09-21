#!/usr/bin/env python3
"""Compatibility entry point; the bot lives in nettadoomer.py."""
import sys
import nettadoomer as _implementation

if __name__ == "__main__":
    raise SystemExit(_implementation.main())
sys.modules[__name__] = _implementation
