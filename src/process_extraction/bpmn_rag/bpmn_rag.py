import os
from dotenv import load_dotenv
import instructor
import pickle

import pandas as pd
import numpy as np
import tiktoken
from openai import OpenAI
from typing import Dict, Any
from process_extraction.bpmn_rag.prompts.qa_prompt import QA_MESSAGES_PROMPT, QA_SYSTEM_PROMPT, QA_REFINE_PROMPT
from opentelemetry.trace import StatusCode
from process_extraction.init_phoenix import init_phoenix
from process_extraction.response_model.Process import ProcessResponse


class BpmnRag:
    """
    Class that implements a version of RAG using BPMNs
    """
    def __init__(self):
        self.client_emb = self.init_client_emb()
        self.client = self.init_client()

    def init_client(self):
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("BASE_URL"))
        client = instructor.from_openai(client, mode=instructor.Mode.JSON)
        return client

    def init_client_emb(self):
        client_emb = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("EMB_BASE_URL"))
        client_emb = instructor.from_openai(client_emb, mode=instructor.Mode.JSON)
        return client_emb
    
    # After: https://learn.microsoft.com/en-us/azure/foundry/openai/tutorials/embeddings 

    def tokenize(self, df_text, token_limit):
        tokenizer = tiktoken.get_encoding("cl100k_base")
        df_text['n_tokens'] = df_text["text"].apply(lambda x: len(tokenizer.encode(x)))
        df_text = df_text[df_text.n_tokens<token_limit]
        return df_text
    
    def create_embedding(self, df_text, token_limit):
        #self.tokenize(df_text, token_limit)
        df_text[os.getenv("EMB_MODEL")] = df_text["text"].apply(lambda x : self.get_embedding(x, model = os.getenv("EMB_MODEL")))
        return df_text


    def get_embedding(self, text, model):
        """
        generate and return embedding with a given model
        
        """
        return self.client_emb.embeddings.create(input = [text], model=model).data[0].embedding
    
    def cosine_similarity(self, a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def search_docs(self,df, user_query, top_n=4):
        model = os.getenv("EMB_MODEL")
        embedding = self.get_embedding(user_query, model=model)
        
        df["similarities"] = df[model].apply(lambda x: self.cosine_similarity(x, embedding))

        res = (df.sort_values("similarities", ascending=False).head(top_n))
        return res
    
    def create_prompt(self, context_str: str,explain_str: str,query_str: str):
        prompt = QA_MESSAGES_PROMPT.format(context_str=context_str,explain_str=explain_str,query_str=query_str)    
        return prompt
    
    def refine_prompt(self, context_str: str,explain_str: str,query_str: str, existing_answer: str):
        prompt = QA_REFINE_PROMPT.format(context_str=context_str,explain_str=explain_str,query_str=query_str,existing_answer=existing_answer)
        return prompt
    
    def query(self, tracer, response_model, user_query, df, context, top_n=4):
        MODEL = os.getenv("MODEL")
        search_res = self.search_docs(df,user_query, top_n)
        prompt = self.create_prompt(context,search_res,user_query)
        
        for i, res in enumerate(search_res):
            with tracer.start_as_current_span("Process", openinference_span_kind="agent") as span:
                span.set_input(prompt)
                
                response = self.client.chat.completions.create(
                    model=MODEL,
                    messages=[
                        {"role": "system", "content": QA_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    response_model=response_model
                )
                span.set_output(response.model_dump())
                span.set_status(StatusCode.OK)
                prompt = self.refine_prompt(context,search_res,user_query,response)
        return response
    
    def open_embedding(self, token_limit):
        df = pd.DataFrame()
        df["text"]=''
        files = os.listdir(os.getenv("DATA_DIRECTORY")+"bpmns")
        data_dump = os.listdir(os.getenv("DATA_DIRECTORY")+"data_dump")
        
        text = ['']

        for filename in files:
            text.append(open(os.getenv("DATA_DIRECTORY")+"bpmn_data.txt").read())
        df["text"]= text
        if len(data_dump)==0:
            df_text = bpmn_rag.create_embedding(df_text=df,token_limit=token_limit)
            with open(os.getenv("DATA_DIRECTORY")+'data_dump/embedding_dump.txt', 'wb') as file:
                pickle.dump(df_text, file)
        else:
            with open(os.getenv("DATA_DIRECTORY")+'data_dump/embedding_dump.txt', 'rb') as file:
                df_text = pickle.load(file)
        return df_text


# Parameters for a run
token_limit = 40000
bpmn_rag = BpmnRag()
tracer = init_phoenix("bpmn_rag")
response_model = ProcessResponse
context = open(os.getenv("DATA_DIRECTORY")+"bpmns/case_base/case_3-7.txt").read()

with open(os.getenv("DATA_DIRECTORY")+'test_dump.txt', 'wb') as testfile:
    pickle.dump(context, testfile)

df_text = bpmn_rag.open_embedding(token_limit)

top_n = 4





def bpmn_rag_task(input: Dict[str, Any]):
    user_request = input["user_request"]
    answer = bpmn_rag.query(
        tracer,
        response_model,
        user_request,
        df_text,
        context,
        top_n)
    return answer
    
if __name__ == "__main__":
    load_dotenv()
    bpmn_rag = BpmnRag()
    #print(os.getenv("DATA_DIRECTORY"))
    #df = pd.read_csv(os.getenv("DATA_DIRECTORY")+'bill_sum_data.csv')
    #df_bills = df[['text', 'summary', 'title']]
    query = "Beschreiben Sie den möglichen Ablauf einer Dienstreiseabrechnung anhand des Diagramms."
    token_limit = 40000
    tracer = init_phoenix("bpmn_rag")
    response_model = ProcessResponse
    context = open(os.getenv("DATA_DIRECTORY")+"context.txt").read()

    text = open(os.getenv("DATA_DIRECTORY")+"bpmn_data.txt").read()
    df = pd.DataFrame()
    df["text"] = [text]

    df_text = bpmn_rag.create_embedding(df_text=df,token_limit=token_limit)
    #df_search = bpmn_rag.search_docs(df=df_text,user_query=query,model=model)
    response = bpmn_rag.query(tracer,response_model,query,df_text,context,4)
    print(response)


    



        
    