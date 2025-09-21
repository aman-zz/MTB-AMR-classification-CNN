#!/usr/bin/env python3
"""
train_tb_model.py
Train a TB drug susceptibility prediction model from ARIBA summary CSVs.

Inputs:
  --summaries_dir   directory containing *_summary.csv files (one per isolate)
  --labels_csv      CSV with columns: sample_id,label (label=0 resistant, 1 susceptible)
  --model_dir       directory to save model + metadata

Outputs in model_dir:
  model.joblib       trained RandomForestClassifier
  features.json      list of features used
  label_map.json     {0: "Resistant", 1: "Susceptible"}
"""

import argparse
import json
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
import joblib

def extract_features(summary_file):
    """Parse ARIBA summary CSV → feature dict (feature_name → value)."""
    df = pd.read_csv(summary_file)
    features = {}
    for _, row in df.iterrows():
        # Create feature name from gene + variant (fallback to row index if missing)
        gene = str(row.get("gene", "NA"))
        var = str(row.get("var", row.name))
        feat_name = f"{gene}:{var}"
        # Mark as present if 'variant_present' exists and true, else fallback
        if "variant_present" in row:
            val = int(bool(row["variant_present"]))
        else:
            # fallback: presence if non-null 'ref_seq' or 'reads'
            val = int(not pd.isna(row.get("ref_seq")) or not pd.isna(row.get("reads")))
        features[feat_name] = val
    return features

def build_dataset(summaries_dir, labels_csv):
    labels_df = pd.read_csv(labels_csv)
    label_map = dict(zip(labels_df.sample_id, labels_df.label))
    all_features = {}
    X, y, sample_ids = [], [], []
    for file in Path(summaries_dir).glob("*_summary.csv"):
        sid = file.stem.replace("_summary", "")
        if sid not in label_map:
            continue
        feats = extract_features(file)
        for f in feats:
            all_features[f] = True
        X.append(feats)
        y.append(label_map[sid])
        sample_ids.append(sid)
    feature_list = sorted(all_features.keys())
    mat = np.zeros((len(X), len(feature_list)), dtype=int)
    for i, feats in enumerate(X):
        for f, v in feats.items():
            if f in all_features:
                j = feature_list.index(f)
                mat[i, j] = v
    return mat, np.array(y), sample_ids, feature_list

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--summaries_dir", required=True)
    ap.add_argument("--labels_csv", required=True)
    ap.add_argument("--model_dir", default="tb_model")
    args = ap.parse_args()

    X, y, sids, features = build_dataset(args.summaries_dir, args.labels_csv)

    model = RandomForestClassifier(n_estimators=200, class_weight="balanced", random_state=42)
    model.fit(X, y)

    outdir = Path(args.model_dir)
    outdir.mkdir(exist_ok=True, parents=True)
    joblib.dump(model, outdir / "model.joblib")
    json.dump(features, open(outdir / "features.json", "w"), indent=2)
    json.dump({0: "Resistant", 1: "Susceptible"}, open(outdir / "label_map.json", "w"), indent=2)

    print(f"Model trained on {X.shape[0]} samples, {X.shape[1]} features")
    print(f"Saved to {outdir}")

if __name__ == "__main__":
    main()
