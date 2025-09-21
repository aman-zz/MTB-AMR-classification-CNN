#!/usr/bin/env python3
"""
make_labels.py
Create labels.csv (sample_id,label) from two lists of isolate IDs:
  - resistant.txt   (one isolate ID per line)
  - susceptible.txt (one isolate ID per line)

Label convention:
  Resistant   → 0
  Susceptible → 1

Usage:
  python make_labels.py --resistant resistant.txt --susceptible susceptible.txt --out labels.csv
"""

import argparse
import pandas as pd

def read_list(path):
    with open(path) as f:
        return [line.strip() for line in f if line.strip()]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--resistant", required=True, help="file with resistant isolate IDs")
    ap.add_argument("--susceptible", required=True, help="file with susceptible isolate IDs")
    ap.add_argument("--out", default="labels.csv", help="output CSV filename")
    args = ap.parse_args()

    resistant = read_list(args.resistant)
    susceptible = read_list(args.susceptible)

    rows = []
    for sid in resistant:
        rows.append({"sample_id": sid, "label": 0})
    for sid in susceptible:
        rows.append({"sample_id": sid, "label": 1})

    df = pd.DataFrame(rows)
    df.to_csv(args.out, index=False)
    print(f"labels.csv written with {len(rows)} entries → {args.out}")

if __name__ == "__main__":
    main()
