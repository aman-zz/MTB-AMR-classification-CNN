import os
import subprocess
import json

# out put summary files will be save in dir 'summary_output_full'
def run_summary():
    sra_list = json.load(open("/home/aman/Projects/MTB-AMR-classification-CNN/sample_input_files/uniqueSRA.json"))
    n_sra = len(sra_list)

    for sra in sra_list:
        if not (os.path.isfile("aribaResult_withBam/outRun_" + sra + "/report.tsv")):
            continue
        print(sra)
        cmd = [
            "ariba",
            "summary",
            "summary_output_full/" + sra + "_summary",
            "aribaResult_withBam/outRun_" + sra + "/report.tsv",
            "--preset",
            "all_no_filter",
        ]
        subprocess.call(cmd)


run_summary()
