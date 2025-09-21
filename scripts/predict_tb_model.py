#!/usr/bin/env python3
"""
predict_tb_model.py
Predict TB drug susceptibility from a new ARIBA summary CSV.

Inputs:
  --summary_csv   ARIBA *_summary.csv file
  --model_dir     directory containing model.joblib + features.json

Output:
  Prints prediction + probability
"""

import argparse
import json
import pandas as pd
import numpy as np
import joblib
from pathlib import Path

def extract_features(summary_file):
    df = pd.read_csv(summary_file)
    features = {}
    for _, row in df.iterrows():
        gene = str(row.get("gene", "NA"))
        var = str(row.get("var", row.name))
        feat_name = f"{gene}:{var}"
        if "variant_present" in row:
            val = int(bool(row["variant_present"]))
        else:
            val = int(not pd.isna(row.get("ref_seq")) or not pd.isna(row.get("reads")))
        features[feat_name] = val
    return features

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary_csv", required=True)
    ap.add_argument("--model_dir", default="tb_model")
    args = ap.parse_args()

    model = joblib.load(Path(args.model_dir) / "model.joblib")
    features = json.load(open(Path(args.model_dir) / "features.json"))
    label_map = json.load(open(Path(args.model_dir) / "label_map.json"))

    feats = extract_features(args.summary_csv)
    vec = np.zeros((1, len(features)), dtype=int)
    for f, idx in zip(features, range(len(features))):
        vec[0, idx] = feats.get(f, 0)

    proba = model.predict_proba(vec)[0,1]
    pred = int(proba >= 0.5)
    print(f"Prediction: {label_map[str(pred)]} (probability susceptible={proba:.3f})")

if __name__ == "__main__":
    main()
