import pandas as pd
import os

def construct_dataset():
    data_dir = os.path.join("src", "process_extraction", "local_data")
    requests = pd.read_csv(os.path.join(data_dir, "requests.csv"), sep=";", header=0)
    
    dataset = []
    
    for i, row in requests.iterrows():

        user_request = row["user_request"]
        ground_truth = row["ground_truth"]
        data = open(os.path.join(data_dir, row["data_file"]), encoding="utf-8", errors="ignore")
        process_data = data.read()
        dataset.append({
            "user_request": user_request,
            "process_data": process_data,
            "ground_truth": ground_truth
        })
    return dataset