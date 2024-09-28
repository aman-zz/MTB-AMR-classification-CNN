import subprocess
import json
import os
from argparse import ArgumentParser
from argparse import RawTextHelpFormatter
import psutil
from concurrent.futures import ThreadPoolExecutor

def main():
    file_sra, out_dir = getArgs()
    # load a list of unique SRA accessions from a jason file, which you want
    # to download their fastq files
    sra_list = json.load(open(file_sra))
    threads_count = psutil.cpu_count() - 2

    with ThreadPoolExecutor(max_workers=threads_count) as executor:
        for sra in sra_list:
            executor.submit(getfastq, sra, out_dir, threads_count)

def getArgs():
    parser = ArgumentParser(
        formatter_class=RawTextHelpFormatter,
        prog="fasterq_download.py",
        description="Execute fasterq-dump call for given list of SRAs.",
    )
    parser.add_argument("-f", "--fSRAs", dest="fileSRAs")

    parser.add_argument("-o", "--oDir", dest="outDir")
    args = parser.parse_args()
    f_sra = args.fileSRAs
    o_dir = args.outDir

    return f_sra, o_dir


def getfastq(sra, out_dir, threads_count):
    # run fasterq-dump from sra toolkit to download fastq files
    cmd = [
        "fasterq-dump",  # if you set sra toolkit's path to PATH, call fasterq-dump directly
        sra,
        "--threads",
        str(threads_count),
        "-O",
        out_dir,  # directory where you want to save the fastq files
    ]
    # when it is not the first run, it tries to download missing fastq files
    f_file1 = out_dir + "/" + sra + "_1.fastq"
    f_file2 = out_dir + "/" + sra + "_2.fastq"
    if not (os.path.isfile(f_file1) and os.path.isfile(f_file2)):
        print("\n--- API Call for {} ---\n".format(sra))
        with open("fastqDumpLog.txt", "a+") as f:
            subprocess.call(cmd)


if __name__ == "__main__":
    main()
