
import os

from process_extraction.bpmn_rag.bpmn_rag import bpmn_rag_task
from process_extraction.standardized_test.test import RAGTest

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

if __name__ == "__main__":
    run_bpmn_rag_test()
