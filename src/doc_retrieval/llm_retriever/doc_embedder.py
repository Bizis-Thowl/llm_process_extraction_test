import os
import pickle

import instructor
from openai import OpenAI
from langchain_mongodb import MongoDBAtlasVectorSearch
from pymongo import MongoClient

import pandas as pd

class DocEmbedder:

    def __init__(self):
        self.client_emb = self.init_client_emb()
        #self.client = self.init_client()

    def init_client_emb(self):
        client_emb = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("EMB_BASE_URL"))
        client_emb = instructor.from_openai(client_emb, mode=instructor.Mode.JSON)
        return client_emb
    
    def init_mongodb_client(self, db_name, collection_name, embeddings, documents):
        MONGODB_ATLAS_CLUSTER_URI = os.getenv("MONGODB_ATLAS_CLUSTER_URI")
        self.mongodb_client = MongoClient(MONGODB_ATLAS_CLUSTER_URI)
        self.MONGODB_COLLECTION = self.mongodb_client[db_name][collection_name]


    def create_embedding(self, df_text): #, index_name
        #self.tokenize(df_text, token_limit)
        df_emb = pd.DataFrame(columns=['name','embeddings'])
        for i,row in df_text.iterrows():
            print("------------------------------------------------------------")
            print(f"Starting with document {row['name']} - ({i}/{len(df_text)}):")
            chunks = row['chunks']
            embeddings = []
            for chunk in chunks:
                print(f"Now embedding {chunk.metadata} of document {row['name']}")
                embeddings.append(self.get_embedding(chunk.page_content, model = os.getenv("EMB_MODEL")))
                
            #embeddings = chunks.apply(lambda x : self.get_embedding(x[1], model = os.getenv("EMB_MODEL")))
            df_emb.loc[i] = [row['name'],embeddings]
        #df_text[os.getenv("EMB_MODEL")] = df_text["text"].apply(lambda x : self.get_embedding(x, model = os.getenv("EMB_MODEL")))
        """
        vector_store = MongoDBAtlasVectorSearch(
            embedding=embeddings,
            collection=self.MONGODB_COLLECTION,
            index_name=index_name,
            relevance_score_fn="cosine",
        )
        ids = vector_store.add_documents(documents=chunks)
        """
        return df_text, df_emb


    def get_embedding(self, text, model):
        """
        generate and return embedding with a given model
        
        """
        return self.client_emb.embeddings.create(input = [text], model=model).data[0].embedding

    def open_embedding(self, df_text = None):
        data_dump = os.listdir(os.getenv("RETRIEVER_DIRECTORY")+"data_dump")

        if len(data_dump)==0:
            output = self.create_embedding(df_text=df_text)
            with open(os.getenv("RETRIEVER_DIRECTORY")+'data_dump/embedding_dump.txt', 'wb') as file:
                pickle.dump(output, file)
        else:
            with open(os.getenv("RETRIEVER_DIRECTORY")+'data_dump/embedding_dump.txt', 'rb') as file:
                output = pickle.load(file)
        return output