#!/usr/bin/env python3
# fasterq_download.py (improved)
import subprocess
import json
import os
import time
import logging
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import psutil
import runAribaInLoop_withBam as ariba_runner

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")


def load_sra_list(path):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"SRA list file not found: {path}")
    # support either json list or newline-separated file with "..." entries
    try:
        data = json.load(p.open())
        if isinstance(data, list):
            return data
    except Exception:
        text = p.read_text().strip().splitlines()
        # tolerant extraction of quoted accessions
        out = []
        for t in text:
            t = t.strip()
            if not t:
                continue
            if t.startswith('"') and '"' in t[1:]:
                out.append(t.split('"')[1])
            else:
                out.append(t)
        return out
    return []


def run_fasterq_dump(sra, out_dir, threads_count, retries=2, wait=5):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    f1 = out_dir / f"{sra}_1.fastq"
    f2 = out_dir / f"{sra}_2.fastq"
    if f1.exists() and f2.exists():
        logging.info("%s: fastq pair already exists, skipping download", sra)
        return True

    cmd = ["fasterq-dump", sra, "--threads", str(threads_count), "-O", str(out_dir)]
    for attempt in range(1, retries + 2):
        logging.info("%s: running fasterq-dump attempt %d: %s", sra, attempt, " ".join(cmd))
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            logging.warning("%s: fasterq-dump failed on attempt %d: %s", sra, attempt, str(e))
            if attempt <= retries:
                logging.info("%s: retrying after %d seconds...", sra, wait)
                time.sleep(wait)
                continue
            else:
                logging.error("%s: all fasterq-dump attempts failed", sra)
                return False
        # success - ensure both files exist
        if f1.exists() and f2.exists():
            logging.info("%s: download complete", sra)
            return True
        else:
            logging.warning("%s: expected fastq pair not found after fasterq-dump", sra)
            return False


def process_sra(sra, out_dir, ariba_out_dir, threads_count, delete, ariba_run):
    ariba_out = Path(ariba_out_dir) / f"outRun_{sra}"
    report = ariba_out / "report.tsv"
    if report.exists():
        logging.info("%s: ARIBA report already exists (%s), skipping ARIBA.", sra, report)
    else:
        ok = run_fasterq_dump(sra, out_dir, threads_count)
        if ok and ariba_run:
            try:
                ariba_runner.runAriba(sra, out_dir, ariba_out_dir)
            except Exception as e:
                logging.exception("%s: ariba_runner.runAriba raised an exception: %s", sra, e)
    # cleanup fastq files if present to save space
    for ext in ("_1.fastq", "_2.fastq"):
        p = Path(out_dir) / f"{sra}{ext}"
        if p.exists() and delete:
            try:
                p.unlink()
                logging.info("%s: removed %s", sra, p.name)
            except Exception:
                logging.exception("%s: failed to remove %s", sra, p)


def main():
    parser = ArgumentParser(prog="fasterq_download.py", description="Download FASTQ for SRAs and run ARIBA.")
    parser.add_argument("-f", "--fSRAs", required=True, help="SRA list (json list or newline file)")
    parser.add_argument("-o", "--oDir", required=True, help="Directory to write fastq (temporary)")
    parser.add_argument("-a", "--ariba_out", default="aribaResult_withBam", help="ARIBA output directory")
    parser.add_argument("-t", "--threads", type=int, default=max(1, psutil.cpu_count() - 2), help="Threads per fasterq-dump")
    parser.add_argument("-w", "--workers", type=int, default=4, help="Concurrent SRAs to process")
    parser.add_argument("--delete", action="store_true", help="Delete downloaded files after processing (default: False)")
    parser.add_argument("--ariba_run", action="store_true", help="Run ariba after isotope download (default: False)")


    args = parser.parse_args()

    sra_list = load_sra_list(args.fSRAs)
    logging.info("Loaded %d SRA accessions", len(sra_list))

    with ThreadPoolExecutor(max_workers=args.workers) as exe:
        futures = [exe.submit(process_sra, sra, args.oDir, args.ariba_out, args.threads, args.delete, args.ariba_run) for sra in sra_list]
        for fut in as_completed(futures):
            try:
                fut.result()
            except Exception:
                logging.exception("Processing a SRA failed")


if __name__ == "__main__":
    main()
