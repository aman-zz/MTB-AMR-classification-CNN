#!/usr/bin/env python3
"""
filter_lines.py
Given two files:
  - file1: list of keys (one per line)
  - file2: lines of data (line-separated)
For each key in file1, search file2 and copy matching lines to output.

Usage:
  python filter_lines.py --file1 keys.txt --file2 data.txt --out matched.txt
"""

import argparse

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file1", required=True, help="file with keys (one per line)")
    ap.add_argument("--file2", required=True, help="file with data lines")
    ap.add_argument("--out", default="matched.txt", help="output file")
    args = ap.parse_args()

    # Load keys into a set for fast search
    keys = set(line.strip() for line in open(args.file1) if line.strip())

    matched = []
    with open(args.file2) as f:
        for line in f:
            if any(key in line for key in keys):  # substring match
                matched.append(line)

    with open(args.out, "w") as out:
        out.writelines(matched)

    print(f"Found {len(matched)} matching lines → {args.out}")

if __name__ == "__main__":
    main()
