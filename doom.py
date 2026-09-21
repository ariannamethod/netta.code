#!/usr/bin/env python3
"""Compatibility entry point; the bot lives in doomer.py."""
import sys
import doomer as _implementation

if __name__ == "__main__":
    raise SystemExit(_implementation.main())
sys.modules[__name__] = _implementation
