
from doc_retrieval.llm_retriever.doc_retriever import Retriever_Controller
from typing import Any, Dict


def doc_retrieval_task(input: Dict[str, Any]):
    user_request = input["user_request"]
    answer = Retriever_Controller.retriever_simple_query(user_request)
    return answer