from openai import OpenAI
import os
from dotenv import load_dotenv
import instructor

from process_extraction.experimentation.prompts.correctness import CORRECTNESS_PROMPT
from process_extraction.experimentation.response_models.correctness import KorrektheitResponse

load_dotenv()

MODEL = os.getenv("MODEL")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("BASE_URL"))
client = instructor.from_openai(client, mode=instructor.Mode.JSON)


def correctness(input: dict, output: dict) -> bool:

    #print("starting eval")

    ground_truth = input.get("ground_truth")
    user_request = input.get("user_request")
    # Last message contains the answer
    response = output.get("final_answer")

    datapoint = {
        "user_request": user_request,
        "correct_answer": ground_truth,
        "generated_answer": response,
    }

    messages = [{"role": "system", "content": CORRECTNESS_PROMPT.format(**datapoint)}]

    response = client.chat.completions.create(
        model=MODEL, messages=messages, response_model=KorrektheitResponse
    )

    return response.ist_korrekt

def site_correctness(input: dict, output: dict) -> bool:
    true_url = input.get("true_url")
    response = output.get("url")

    return true_url == response
