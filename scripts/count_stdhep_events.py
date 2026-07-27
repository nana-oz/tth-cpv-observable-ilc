#!/usr/bin/env python3
"""Count physics events that can actually be read from one STDHEP file.

This scans the file to EOF without creating an SLCIO copy. The final count is
the file's readable N_written, not the number requested in a generator job.

Usage:
    python3 scripts/count_stdhep_events.py /path/to/file.stdhep
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ilc_tth_cpv.slcio import open_stdhep  # noqa: E402


def count_readable_events(reader, progress_every: int = 0) -> int:
    count = 0
    while True:
        try:
            event = reader.readEvent()
        except Exception as exc:
            raise RuntimeError(
                f"read failed after {count} readable events: {exc}"
            ) from exc
        # cppyy represents the LCIO EOF null pointer as a false proxy rather
        # than Python None in the current NAF stack.
        if event is None or not event:
            return count
        count += 1
        if progress_every > 0 and count % progress_every == 0:
            print(f"read {count} events...", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stdhep", type=Path, help="STDHEP file to scan")
    parser.add_argument(
        "--progress-every",
        type=int,
        default=10000,
        help="print progress every N events; 0 disables progress (default: 10000)",
    )
    args = parser.parse_args()

    if not args.stdhep.is_file():
        raise SystemExit(f"STDHEP file not found: {args.stdhep}")
    if args.progress_every < 0:
        raise SystemExit("--progress-every must be non-negative")

    reader = open_stdhep(args.stdhep)
    try:
        count = count_readable_events(reader, args.progress_every)
    except Exception as exc:
        raise SystemExit(
            f"STDHEP scan failed for {args.stdhep}: {exc}"
        ) from exc

    print(f"stdhep          : {args.stdhep}")
    print(f"readable_events : {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
