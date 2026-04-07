import os
from dotenv import load_dotenv
import instructor



import numpy as np
#import tiktoken
from openai import OpenAI
#from typing import Dict, Any
from opentelemetry.trace import StatusCode

from doc_retrieval.llm_retriever.prompts.qa_prompt import QA_SYSTEM_PROMPT, QA_RAG_PROMPT, SELECTION_SYSTEM_PROMPT
from doc_retrieval.llm_retriever.doc_chunker import DocChunker
from doc_retrieval.llm_retriever.doc_embedder import DocEmbedder
from doc_retrieval.llm_retriever.response_model.Retriever import URLRetrievalResponse, URLSelectionResponse

from process_extraction.init_phoenix import init_phoenix
#from process_extraction.response_model.Process import ProcessResponse

class DocRetriever:

    """
    Retrieval of documents making use of LLMs. 
    """
    def __init__(self):
        #self.client_emb = self.init_client_emb()
        self.client = self.init_client()
        self.tracer = init_phoenix()

    def init_client(self):
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("BASE_URL"))
        client = instructor.from_openai(client, mode=instructor.Mode.JSON)
        return client
    """
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
    """
    def cosine_similarity(self, a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def search_docs(self,df, user_query, top_n=4):
        model = os.getenv("EMB_MODEL")
        embedding = self.get_embedding(user_query, model=model)
        
        df["similarities"] = df[model].apply(lambda x: self.cosine_similarity(x, embedding))

        res = (df.sort_values("similarities", ascending=False).head(top_n))
        return res
    
    
    def create_prompt(self, search_result: str, query_str: str):
        prompt = QA_RAG_PROMPT.format(search_result,query_str=query_str)    
        return prompt
    """
    def refine_prompt(self, context_str: str,explain_str: str,query_str: str, existing_answer: str):
        prompt = QA_REFINE_PROMPT.format(context_str=context_str,explain_str=explain_str,query_str=query_str,existing_answer=existing_answer)
        return prompt
    """

    def query(self, user_query, df, response_model = URLRetrievalResponse): #context,
        MODEL = os.getenv("MODEL")
        search_res = self.search_docs(df,user_query, top_n=3)
        prompt = QA_RAG_PROMPT.format(user_query = user_query,
                                      chunk_1 =search_res[0],
                                      chunk_2 =search_res[1],
                                      chunk_3 =search_res[2])
        
        for i, res in enumerate(search_res):
            with self.tracer.start_as_current_span("Process", openinference_span_kind="agent") as span:
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
                #prompt = self.refine_prompt(context,search_res,user_query,response)
        return response
    
    def query_select(self, user_query, df, top_n = 4, response_model = URLSelectionResponse):
        MODEL = os.getenv("MODEL")
        search_res = self.search_docs(df,user_query, top_n)
        prompt = self.create_prompt(search_res,user_query)
        for i, result in search_res:
            with self.tracer.start_as_current_span("Process", openinference_span_kind="agent") as span:
                span.set_input(prompt)
                
                response = self.client.chat.completions.create(
                    model=MODEL,
                    messages=[
                        {"role": "system", "content": SELECTION_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    response_model=response_model
                )
                span.set_output(response.model_dump())
                span.set_status(StatusCode.OK)
        return response

if __name__ == "__main__":
    load_dotenv()
    #tracer = init_phoenix("doc_retriever")
    chunker = DocChunker()
    HTML_DIRECTORY = os.getenv("HTML_DIRECTORY")
    df_text = chunker.get_chunks(chunker.get_docs(HTML_DIRECTORY))
    embedder = DocEmbedder()
    #embedder.init_mongodb_client()
    df_text = embedder.open_embedding(df_text)
    retriever = DocRetriever()

    response_model = URLRetrievalResponse
    user_query = "Wie kann ich mein Passwort zurücksetzen?"
