import os
import subprocess
import shlex
from argparse import ArgumentParser
from argparse import RawTextHelpFormatter
from joblib import Parallel, delayed


def main():
    file_sra, in_dir, out_dir, n_j, dry_run = getArgs()
    sra_list = loadAccessions(file_sra)
    Parallel(n_jobs=n_j, prefer="threads")(
        delayed(runAriba)(sra, in_dir, out_dir, dry_run) for sra in sra_list
    )


def loadAccessions(file_sra):
    """
    Loads in list of SRA accession numbers from file_sra.
    Supports:
      - Plain text files (one accession per line)
      - JSON files (list or dict with accessions)
    """
    import json
    # Try to detect file type by extension
    if file_sra.endswith('.json'):
        with open(file_sra) as f:
            data = json.load(f)
            # If it's a dict, get values; if list, use directly
            if isinstance(data, dict):
                sra_list = list(data.values())
            else:
                sra_list = data
    else:
        with open(file_sra) as f:
            sra_list = [line.strip() for line in f if line.strip()]
    # Clean up SRA names: remove quotes, commas, and whitespace
    cleaned = []
    for sra in sra_list:
        sra = str(sra).strip().replace('"','').replace("'","").replace(",","")
        cleaned.append(sra)
    return cleaned


def getArgs():
    parser = ArgumentParser(
        formatter_class=RawTextHelpFormatter,
        prog="runAribaInLoop_withBam.py",
        description="Run ARIBA for isolates to output variant report files and intermediate results.\n\nExample usage:\n  python runAribaInLoop_withBam.py -f output.json -i /path/to/fastqDir -o ./aribaResult/ -c 'ariba run out.card.prepareref {input1} {input2} {output}' -n 8 --dry_run\n",
    )
    parser.add_argument("-f", "--file", dest="fileSRAs", required=True, help="Path to file containing SRA accession list (JSON or TXT)")
    parser.add_argument("-i", "--input_dir", dest="inDir", required=True, help="Directory containing input FASTQ files")
    parser.add_argument("-o", "--output_dir", dest="outDir", required=True, help="Directory to store ARIBA results")
    parser.add_argument("-n", "--n_jobs", dest="nJobs", type=int, default=1, help="Number of parallel jobs (default: 1)")
    parser.add_argument("--dry_run", action="store_true", help="Print commands without executing them")
    args = parser.parse_args()
    return args.fileSRAs, args.inDir, args.outDir, args.nJobs, args.dry_run


def runAriba(sra, in_dir, out_dir, dry_run):
    sra = sra.strip()
    fastq_dir = os.path.join(in_dir, "")
    reads1 = os.path.join(fastq_dir, f"{sra}_1.fastq")
    reads2 = os.path.join(fastq_dir, f"{sra}_2.fastq")
    out_run_dir = os.path.join(out_dir, f"outRun_{sra}")
    print(f"[DEBUG] Checking: '{reads1}' and '{reads2}'")
    if os.path.isfile(reads1) and os.path.isfile(reads2):
        if not os.path.isfile(os.path.join(out_run_dir, "report.tsv")):
            if os.path.isdir(out_run_dir):
                subprocess.run(["rm", "-r", out_run_dir])
            # Always use a list for ARIBA command
            cmd = [
                "ariba", "run", "out1.card.prepareref", reads1, reads2, out_run_dir
            ]
            print(f"[INFO] Running: {' '.join(cmd)}")
            if not dry_run:
                with open("./aribaRunLog.txt", "a+") as f:
                    subprocess.call(cmd)
    else:
        print(f"[ERROR] Invalid path: {reads1} or {reads2}")
        with open("./sra_paired_read_notFound.txt", "a+") as l:
            l.write(sra + "\n")


if __name__ == "__main__":
    main()
