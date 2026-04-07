import os

#from bs4 import BeautifulSoup
import pandas as pd
from dotenv import load_dotenv

from langchain_text_splitters import HTMLSectionSplitter #, HTMLSemanticPreservingSplitter, RecursiveCharacterTextSplitter HTMLHeaderTextSplitter, 

class DocChunker:

    def __init__(self):
        pass
    
    def chunk_doc(self, html, h_to_split=[("h1", "Header 1"),("h2", "Header 2")]):
        html_splitter = HTMLSectionSplitter(h_to_split)
        html_header_splits = html_splitter.split_text(html)
        return html_header_splits
    
    def get_docs(self,dir,df_text = pd.DataFrame(columns =['name','text'])):
        for file in os.scandir(dir):
            if file.is_dir():
                self.get_docs(file.path, df_text)
            else:
                with open(file.path, "r", encoding = 'UTF8',errors='ignore') as f:
                    #soup = BeautifulSoup(f, "html.parser")
                    f_name = os.path.basename(os.path.dirname(file.path))
                    df_text.loc[len(df_text)]= [f_name,f.read()]
                    #df_text['name'].append(f.name)
                    #df_text['text'].append(f.read)
                
        return df_text

    def get_chunks(self, df_text):
        chunks = []
        for i,row in df_text.iterrows():
            #name = row['name']
            text = row['text']
            chunks.append(self.chunk_doc(text,h_to_split=[("h1", "Header 1"),("h2", "Header 2")]))
            #chunks[name]= 
        df_text['chunks'] = chunks
        #print(df_text)
        return df_text

if __name__ == "__main__":
    load_dotenv()
    chunker = DocChunker()
    HTML_DIRECTORY = os.getenv("HTML_DIRECTORY","value does not exist")
    print(HTML_DIRECTORY)
    docs = chunker.get_docs(HTML_DIRECTORY)
    chunks = chunker.get_chunks(docs)
    #print(chunks)