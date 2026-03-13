import os
from dotenv import load_dotenv
import instructor

import os
import pandas as pd
import numpy as np
import tiktoken
from openai import OpenAI


class BpmnRag:
    """
    Class that implements a version of RAG using BPMNs
    """
    def __init__(self):
        self.client = self.init_client()

    def init_client():
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("BASE_URL"))
        client = instructor.from_openai(client, mode=instructor.Mode.JSON)
        return client
    
    # After: https://learn.microsoft.com/en-us/azure/foundry/openai/tutorials/embeddings 

    def get_embedding(self, text, model):
        """
        generate and return embedding with a given model
        
        """
        return self.client.embeddings.create(input = [text], model=model).data[0].embedding
    
    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def search_docs(self,df, user_query, model, top_n=4, to_print=True, ):
        embedding = self.get_embedding(user_query, model=model)
        
        df["similarities"] = df.ada_v2.apply(lambda x: self.cosine_similarity(x, embedding))

        res = (df.sort_values("similarities", ascending=False).head(top_n))
        return res
    
if __name__ == "__main__":
    print("")
    bpmn_rag = BpmnRag
    bpmn_rag.search_docs()

    



        
    