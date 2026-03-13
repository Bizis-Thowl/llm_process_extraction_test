import pandas as pd
import asyncio
import os

import graphrag.api as api
from graphrag.config.load_config import load_config
from typing import Dict, Any

graphrag_config = load_config(os.getenv("PROJECT_DIRECTORY"))
PROJECT_DIRECTORY = os.getenv("PROJECT_DIRECTORY")

try:
    entities = pd.read_parquet(f"{PROJECT_DIRECTORY}/output/entities.parquet")
    communities = pd.read_parquet(f"{PROJECT_DIRECTORY}/output/communities.parquet")
    text_unit_df = pd.read_parquet(f"{PROJECT_DIRECTORY}/output/text_units.parquet")
    relationships = pd.read_parquet(f"{PROJECT_DIRECTORY}/output/relationships.parquet")
    community_reports = pd.read_parquet(f"{PROJECT_DIRECTORY}/output/community_reports.parquet")
except:
    print("Warning: The graph data could not be read. You first have to index the graph!")

# Set of methods that define the four different approaches in GraphRAG as tasks for the arize-phoenix pipeline

def task_local(input: Dict[str, Any]):
    user_request = input["user_request"]
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

def task_global(input: Dict[str, Any]):
    user_request = input["user_request"]
    final_answer, context = asyncio.run(api.global_search(
            config=graphrag_config,
            entities=entities,
            communities=communities,
            community_reports=community_reports,
            community_level=2,
            dynamic_community_selection= True,
            response_type="Kurze präzise Antwort auf Deutsch",
            query=user_request
        ))
    return {"final_answer": final_answer, "context": context}    

def task_basic(input: Dict[str, Any]):
    user_request = input["user_request"]
    final_answer, context = asyncio.run(api.basic_search(
            config=graphrag_config,
            text_units= text_unit_df,
            response_type="Kurze präzise Antwort auf Deutsch",
            query=user_request
        ))
    return {"final_answer": final_answer, "context": context}

def task_drift(input: Dict[str, Any]):
    user_request = input["user_request"]
    final_answer, context = asyncio.run(api.drift_search(
            config=graphrag_config,
            entities=entities,
            communities=communities,
            community_reports=community_reports,
            text_units= text_unit_df,
            relationships= relationships,
            community_level=2,
            response_type="Kurze präzise Antwort auf Deutsch",
            query=user_request
        ))
    return {"final_answer": final_answer, "context": context}