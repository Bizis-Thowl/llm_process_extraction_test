import os

import asyncio

import graphrag.api as api
import pandas as pd
from graphrag.config.load_config import load_config
from graphrag.index.typing.pipeline_run_result import PipelineRunResult
from typing import Dict, Any

from phoenix.client import Client
from phoenix.experiments import run_experiment
#from process_extraction.experimentation.construct_dataset import construct_dataset
from process_extraction.experimentation.evaluators.correctness import correctness
from process_extraction.init_phoenix import init_phoenix
#from process_extraction.process_extraction_decomposition import decompose_ask_about_process

tracer = init_phoenix("llm-process-extraction-graphrag")

graphrag_config = load_config(os.getenv("PROJECT_DIRECTORY"))
PROJECT_DIRECTORY = os.getenv("PROJECT_DIRECTORY")

entities = pd.read_parquet(f"{PROJECT_DIRECTORY}/output/entities.parquet")
communities = pd.read_parquet(f"{PROJECT_DIRECTORY}/output/communities.parquet")
text_unit_df = pd.read_parquet(f"{PROJECT_DIRECTORY}/output/text_units.parquet")
relationships = pd.read_parquet(f"{PROJECT_DIRECTORY}/output/relationships.parquet")
community_reports = pd.read_parquet(f"{PROJECT_DIRECTORY}/output/community_reports.parquet")

async def run_queries(df_qa):
    # Retrieve Questions and Answers
    
    # Get graph context
    entities = pd.read_parquet(f"{PROJECT_DIRECTORY}/output/entities.parquet")
    communities = pd.read_parquet(f"{PROJECT_DIRECTORY}/output/communities.parquet")
    text_unit_df = pd.read_parquet(f"{PROJECT_DIRECTORY}/output/text_units.parquet")
    relationships = pd.read_parquet(f"{PROJECT_DIRECTORY}/output/relationships.parquet")
    community_reports = pd.read_parquet(f"{PROJECT_DIRECTORY}/output/community_reports.parquet")
    
    # Query locally
    df_graphrag = []
    for i, row in df_qa.iterrows():
        user_request = row["user_request"]
        ground_truth = row["ground_truth"]
        #
        response, context = await api.local_search(
            config=graphrag_config,
            entities=entities,
            communities=communities,
            community_reports=community_reports,
            text_units= text_unit_df,
            relationships= relationships,
            covariates = None,
            community_level=2,
            response_type="Kurze präzise Antwort auf Deutsch",
            query=user_request
        )
        df_graphrag.append({
            "user_request": user_request,
            "process_data": response,
            "ground_truth": ground_truth
        })
    
    return df_graphrag

def task(input: Dict[str, Any]):
    user_request = input["user_request"]
    process_data = input["process_data"]
    final_answer, context = asyncio.run(api.local_search(
            config=graphrag_config,
            entities=entities,
            communities=communities,
            community_reports=community_reports,
            text_units= text_unit_df,
            relationships= relationships,
            covariates = None,
            community_level=2,
            response_type="Kurze präzise Antwort auf Deutsch",
            query=user_request
        ))
    return {"final_answer": final_answer, "context": context}

async def experiment(dataset_name, loc_qa_dataset):
    px_client = Client()
    df_qa = pd.read_csv(loc_qa_dataset, sep =";")
    #data =  await run_queries(df_qa)
    dataset_df = pd.DataFrame(df_qa)

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

def index_graph():
    index_result : list[PipelineRunResult] = api.build_index(
        config=graphrag_config,)
    # index_result is a list of workflows that make up the indexing pipeline that was run
    for workflow_result in index_result:
        status = f"error\n{workflow_result.error}" if workflow_result.error else "success"
        print(f"Workflow Name: {workflow_result.workflow}\tStatus: {status}")

if __name__ == "__main__":
    loc_qa_dataset = 'Fragen_Antworten_Dienstreise.csv'
    dataset_name = "graphrag_evaluation"
    asyncio.run(experiment(dataset_name,loc_qa_dataset))