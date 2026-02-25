from openai import OpenAI
import os
from dotenv import load_dotenv
import instructor
from response_model.Process import ProcessResponse
from prompts.process_prompt import PROCESS_PROMPT
from init_phoenix import init_phoenix
from opentelemetry.trace import StatusCode
import pandas as pd
load_dotenv()

MODEL = os.getenv("MODEL")

def ask_about_process(tracer, prompt, response_model):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("BASE_URL"))
    client = instructor.from_openai(client)
    
    with tracer.start_as_current_span("Process", openinference_span_kind="agent") as span:
        span.set_input(prompt)
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Du bist ein hilfreicher Assistent. Gib kurze, präzise Antworten"},
                {"role": "user", "content": prompt}
            ],
            response_model=response_model
        )
        span.set_output(response.model_dump())
        span.set_status(StatusCode.OK)
    return response

def create_prompt(user_request: str, process_data: str):
    prompt = PROCESS_PROMPT.format(user_request=user_request, process_data=process_data)
    return prompt

def test_model(tracer, response_model, MODEL=os.getenv("MODEL")):
    requests = pd.read_csv("local_data/requests.csv", header=0)
    # Iterate over every request stored in local_data/requests.csv
    # The folder "local_data" and its contents have to be created manually before running this file
    for i, row in requests.iterrows():

        user_request = row["user_request"]

        # Accessing the data, the model has to work with
        
        data = open("local_data/"+row["data_file"], encoding='utf-8')
        process_data=data.read()

        prompt = PROCESS_PROMPT.format(user_request=user_request, process_data=process_data)
        ask_about_process(tracer,prompt, response_model=response_model)
    
    
if __name__ == "__main__":
    
    # Starting the tracer
    tracer = init_phoenix("llm-process-ectraction")

    
    response_model = ProcessResponse

    test_model(tracer=tracer, response_model=response_model)
