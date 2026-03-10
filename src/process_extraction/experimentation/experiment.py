from re import M
from phoenix.client import Client
from phoenix.experiments import run_experiment
import pandas as pd
from typing import Dict, Any
from openai import OpenAI
import os
import instructor

from process_extraction.experimentation.construct_dataset import construct_dataset
from process_extraction.experimentation.evaluators.correctness import correctness
from process_extraction.init_phoenix import init_phoenix
from process_extraction.process_extraction_decomposition import decompose_ask_about_process

dataset_name = "test-dataset"
dataset = construct_dataset()

tracer = init_phoenix("llm-process-extraction-decomposition")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("BASE_URL"))
client = instructor.from_openai(client, mode=instructor.Mode.JSON)

def task(input: Dict[str, Any]):
    user_request = input["user_request"]
    process_data = input["process_data"]
    final_answer = decompose_ask_about_process(tracer, user_request, process_data, client)
    return {"final_answer": final_answer}

def experiment():
    px_client = Client()
    dataset_df = pd.DataFrame(dataset)

    try:
        px_dataset = px_client.datasets.create_dataset(
            dataframe=dataset_df, name=dataset_name, input_keys=["user_request", "process_data", "ground_truth"]
        )
    except Exception as e:
        print(f"Error creating dataset: {e}")
        px_dataset = px_client.datasets.get_dataset(dataset=dataset_name)

    run_experiment(
        px_dataset,
        task,
        evaluators=[correctness],
        timeout=100000000,
        experiment_name="test-experiment",
        experiment_description="This experiment is used to test if the phoenix run_experiment method is correctly implemented",
        concurrency=8
    )


if __name__ == "__main__":
    experiment()
