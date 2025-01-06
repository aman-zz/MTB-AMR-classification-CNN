import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler
import os
import pandas as pd
import get_feature_vector as gfv

def load_model(model_path):
    """Load a saved model from the specified file path."""
    return joblib.load(model_path)

def predict_susceptibility(model, scaler, feature_vector):
    """
    Predict susceptibility using the trained model and scaled features.

    Parameters:
        model: Trained machine learning model.
        scaler: StandardScaler instance used for scaling.
        feature_vector: A 1D array of features for the genome.

    Returns:
        Prediction result (e.g., 0 = resistant, 1 = susceptible).
    """
    # Scale the feature vector
    scaled_features = scaler.transform([feature_vector])

    # Predict using the loaded model
    prediction = model.predict(scaled_features)
    return prediction[0]

def get_model_accuracy(model):
    """
    Get the accuracy of the model from the saved model object.

    Parameters:
        model: Trained machine learning model.

    Returns:
        Accuracy of the model.
    """
    if hasattr(model, 'oob_score_'):
        return model.oob_score_ * 100  # For RandomForest with out-of-bag score
    elif hasattr(model, 'score'):
        # Placeholder: Replace with actual accuracy computation if saved separately
        return "Accuracy not available"
    else:
        return "Accuracy not available"

def main():
    # Define drugs and their corresponding models
    drugL = ["ethambutol", "isoniazid", "pyrazinamide", "rifampicin"]

    # Load new genome features (example: replace with actual file/input source)
    # genome_features = getFeature("ERR2512455")
    genome_features = np.loadtxt("single_featureM_X_ethambutol.txt", dtype="i4")

    # Iterate over each drug and make predictions
    for drug in drugL:
        print(f"\nEvaluating susceptibility for drug: {drug}")

        # Load the saved model and scaler
        model_path = f"random_forest_{drug}.joblib"  # Update to desired model file if needed
        model = load_model(model_path)

        # Load the scaler used during training
        training_features = np.loadtxt(f"featureM_X_{drug}.txt", dtype="i4")
        scaler = StandardScaler()
        scaler.fit(training_features)
        # Ensure the input feature vector matches the training data dimensions
        if genome_features.shape[0] != training_features.shape[1]:
            # If dimensions don't match, pad the feature vector with zeros
            padded_features = np.zeros(training_features.shape[1], dtype=int)
            padded_features[:genome_features.shape[0]] = genome_features
            genome_features = padded_features

        # Predict susceptibility
        prediction = predict_susceptibility(model, scaler, genome_features)

        # Get model accuracy
        accuracy = get_model_accuracy(model)

        if prediction == 1:
            print(f"The genome is susceptible to {drug}.")
        else:
            print(f"The genome is resistant to {drug}.")

        print(f"Model Accuracy: {accuracy}%)")

def getFeature(sra):
    raw_feature = []
    # summary and report files are outputs of ariba, containing reference clusters that are matched by the sample
    # and information about the called variants and detected AMR associated genes respectively
    summary = "summary_output_full/" + sra + "_summary.csv"
    ariba_output = "aribaResult_withBam/outRun_" + sra + "/report.tsv"
    if os.path.isfile(ariba_output):
        df = pd.read_csv(ariba_output, sep="\t")
        df_summary = pd.read_csv(summary, sep=",")
        n_row = len(df)
        for i in range(0, n_row):
            # check if the sample matches the cluster presenting in ith line of report file
            if df_summary[df["cluster"][i] + ".match"][0] == "yes":
                # Add gene present
                if (
                        not (df["ref_name"][i] in raw_feature)
                        and df["known_var"][i] == "."
                ):
                    raw_feature.extend([df["ref_name"][i]])
                # Add novel variant that is located on a coding gene
                if (
                        df["known_var"][i] == "0"
                        and df["gene"][i] == "1"
                        and not (
                        (df["ref_name"][i] + "." + df["ref_ctg_change"][i])
                        in raw_feature
                )
                ):
                    # cov% could be added in sumary. For insertion and deletion, there is no cov %
                    raw_feature.extend(
                        [df["ref_name"][i] + "." + df["ref_ctg_change"][i]]
                    )
                # Add detected know variant
                if (
                        df["known_var"][i] == "1"
                        and df["has_known_var"][i] == "1"
                        and not (
                        (df["ref_name"][i] + "." + df["known_var_change"][i])
                        in raw_feature
                )
                ):
                    raw_feature.extend(
                        [df["ref_name"][i] + "." + df["known_var_change"][i]]
                    )
    return gfv.generate_featureVector_forOneIsoform(raw_feature, summary, ariba_output, sra, gfv.generate_sra_lineage_map("lineage.xls"))
if __name__ == "__main__":
    main()
