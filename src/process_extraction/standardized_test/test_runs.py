
import os

from process_extraction.bpmn_rag.bpmn_rag import bpmn_rag_task
from process_extraction.standardized_test.test import RAGTest
from process_extraction.standardized_test.tasks import doc_retrieval_task

def run_bpmn_rag_test():
    rag_test = RAGTest()

    rag_test.run_rag_experiments(
        runs=5,
        tasks=[bpmn_rag_task],
        loc_qa_dataset = os.getenv("DATA_DIRECTORY")+'Fragen_Antworten_Dienstreise.csv',
        dataset_name = "test-dataset", #bpmnrag_evaluation_v1
        exp_name = "Qwen3-30B-A3B-Instruct",
        exp_description = "This experiment verifies that the standardized test module works"
    )

def run_doc_retrieval_test():
    rag_test = RAGTest()

    rag_test.run_rag_experiments(
        runs = 5,
        tasks=[doc_retrieval_task],
        loc_qa_dataset= "Fragen_Doc_Retrieval.csv",
        dataset_name= "doc_retrieval_evaluation",
        exp_name= "Qwen3-30B-A3B-Instruct",
        exp_description= "Evaluation of the documant retrieval with LLM assistance"
    )

if __name__ == "__main__":
    run_bpmn_rag_test()
