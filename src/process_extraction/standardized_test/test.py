import pandas as pd
import asyncio

from process_extraction.experimentation.evaluators.correctness import correctness, site_correctness
from phoenix.client import Client
from phoenix.experiments import run_experiment

class RAGTest:
    """
    Class for testing RAG-apporaches and LLMs on their RAG-capabilities
    """

    def __init__(self):
        pass

    async def experiment(self,dataset_name, loc_qa_dataset, exp_name, exp_description, task_used):
        px_client = Client()
        df_qa = pd.read_csv(loc_qa_dataset, sep =";")
        #data =  await run_queries(df_qa)
        dataset_df = pd.DataFrame(df_qa)

        # Create the dataset, that is used for the 
        
        try:
            px_dataset = px_client.datasets.get_dataset(dataset=dataset_name)
        except Exception as e:
            print(f"Dataset does not yet exist: {e}")
            print("Creating dataset.")
            px_dataset = px_client.datasets.create_dataset(
                dataframe=dataset_df, name=dataset_name, input_keys=["user_request", "ground_truth"]
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
    
    def run_rag_experiments(self,runs, tasks, loc_qa_dataset,dataset_name,exp_name,exp_description):
        # Method that runs the experiment-method x (runs) times for every task-method it was given 
        for item in tasks:
            exp_name_full = exp_name+"-"+item.__name__
            for i in range(runs):
                asyncio.run(self.experiment(dataset_name,loc_qa_dataset,exp_name_full,exp_description,item))

class RetrievalTest(RAGTest):

    async def experiment(self,dataset_name, loc_qa_dataset, exp_name, exp_description, task_used):
        px_client = Client()
        df_qa = pd.read_csv(loc_qa_dataset, sep =";")
        #data =  await run_queries(df_qa)
        dataset_df = pd.DataFrame(df_qa)

        # Create the dataset, that is used for the 
        
        try:
            px_dataset = px_client.datasets.get_dataset(dataset=dataset_name)
        except Exception as e:
            print(f"Dataset does not yet exist: {e}")
            print("Creating dataset.")
            px_dataset = px_client.datasets.create_dataset(
                dataframe=dataset_df, name=dataset_name, input_keys=["user_request", "ground_truth", "true_url"]
            )
            
        
        run_experiment(
            px_dataset,
            task_used,
            evaluators=[correctness, site_correctness],
            timeout=100000000,
            experiment_name=exp_name,
            experiment_description=exp_description,
            concurrency=8
        )
        
