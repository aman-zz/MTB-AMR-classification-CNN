#!/usr/bin/env python3
# run_summary_inLoop.py (improved)
import os
import subprocess
import json
from pathlib import Path
from argparse import ArgumentParser
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")


def run_summary(sra_list_file="uniqueSRA.json", ariba_out_dir="aribaResult_withBam", summary_dir="summary_output_full"):
    summary_path = Path(summary_dir)
    summary_path.mkdir(parents=True, exist_ok=True)

    try:
        sra_list = json.load(open(sra_list_file))
    except Exception:
        # fallback; each line an accession
        sra_list = [l.strip().strip('"') for l in open(sra_list_file).read().splitlines() if l.strip()]

    for sra in sra_list:
        report = Path(ariba_out_dir) / f"outRun_{sra}" / "report.tsv"
        if not report.exists():
            logging.info("%s: report not found, skipping", sra)
            continue
        out_summary = Path(summary_dir) / f"{sra}_summary"
        cmd = [
            "ariba",
            "summary",
            str(out_summary),
            str(report),
            "--preset",
            "all_no_filter",
        ]
        logging.info("%s: running ariba summary", sra)
        subprocess.call(cmd)


if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument("-f", "--fSRAs", default="uniqueSRA.json", help="SRA list file")
    p.add_argument("-a", "--ariba_out", default="aribaResult_withBam", help="ARIBA output directory")
    p.add_argument("-s", "--summary_out", default="summary_output_full", help="summary output dir")
    args = p.parse_args()
    run_summary(args.fSRAs, args.ariba_out, args.summary_out)
