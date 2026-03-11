import os

import asyncio

import graphrag.api as api
import pandas as pd
from graphrag.config.load_config import load_config
from graphrag.index.typing.pipeline_run_result import PipelineRunResult
#from typing import Dict, Any

from phoenix.client import Client
from phoenix.experiments import run_experiment
from process_extraction.experimentation.evaluators.correctness import correctness
from process_extraction.init_phoenix import init_phoenix

from process_extraction.graphrag_test.tasks import task_basic,task_drift,task_global,task_local

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



async def experiment(dataset_name, loc_qa_dataset, exp_name, exp_description, task_used):
    px_client = Client()
    df_qa = pd.read_csv(loc_qa_dataset, sep =";")
    #data =  await run_queries(df_qa)
    dataset_df = pd.DataFrame(df_qa)

    # Create the dataset, that is used for the 

    px_dataset = px_client.datasets.get_dataset(dataset=dataset_name)
    if px_dataset == None:
        px_dataset = px_client.datasets.create_dataset(
            dataframe=dataset_df, name=dataset_name, input_keys=["user_request", "process_data", "ground_truth"]
        )
    
    try:
        px_dataset = px_client.datasets.get_dataset(dataset=dataset_name)
    except Exception as e:
        print(f"Dataset does not yet exist: {e}")
        print("Creating dataset.")
        px_dataset = px_client.datasets.create_dataset(
            dataframe=dataset_df, name=dataset_name, input_keys=["user_request", "process_data", "ground_truth"]
        )
        
    
    run_experiment(
        px_dataset,
        task_used,
        evaluators=[correctness],
        timeout=100000000,
        experiment_name=exp_name,
        experiment_description=exp_description,
        concurrency=8
    )

def index_graph():
    index_result : list[PipelineRunResult] = api.build_index(
        config=graphrag_config,)
    # index_result is a list of workflows that make up the indexing pipeline that was run
    for workflow_result in index_result:
        status = f"error\n{workflow_result.error}" if workflow_result.error else "success"
        print(f"Workflow Name: {workflow_result.workflow}\tStatus: {status}")

def run_graphrag_experiments(runs, tasks, loc_qa_dataset,dataset_name,exp_name,exp_description):
    # Method that runs the experiment-method x (runs) times for every task-method it was given 
    for item in tasks:
        exp_name_full = exp_name+"-"+item.__name__
        for i in range(runs):
            asyncio.run(experiment(dataset_name,loc_qa_dataset,exp_name_full,exp_description,item))


if __name__ == "__main__":
    # Variables to change for the experiment runs
    loc_qa_dataset = 'Fragen_Antworten_Dienstreise.csv'
    dataset_name = "graphrag_evaluation"
    exp_name = "qwen3-8b-40k" # old: test-experiment
    exp_description = "This experiment is used to evaluate the GraphRAG approach for the model "+exp_name
    task_used = task_local
    tasks = [task_local,task_global,task_basic,task_drift]
    runs = 5

    # Run the experiments with the given variables
    run_graphrag_experiments(runs,tasks,loc_qa_dataset,dataset_name,exp_name,exp_description)
    
    #asyncio.run(experiment(dataset_name,loc_qa_dataset,exp_name,exp_description,task_used))