from openai import OpenAI
import os
from dotenv import load_dotenv
import instructor
from response_model.Process import ProcessResponse
from prompts.decomposition_prompt import DECOMPOSITION_PROMPT
from prompts.final_answer_prompt import FINAL_ANSWER_PROMPT
from prompts.solve_subquestion_prompt import SOLVE_SUBQUESTION_PROMPT
from init_phoenix import init_phoenix
from opentelemetry.trace import StatusCode
import pandas as pd
from response_model.Decomposition import SubQuestionWithAnswer, SubQuestion
from typing import Iterable

load_dotenv()

MODEL = os.getenv("MODEL")


def decompose_ask_about_process(tracer, user_request, process_data, client):

    with tracer.start_as_current_span(
        "Process", openinference_span_kind="agent"
    ) as span:
        span.set_input("start decomposition of user request")

        subquestions = decompose_question(tracer, user_request, process_data, client)
        solved_questions = solve_subquestions(
            tracer, subquestions, user_request, process_data, client
        )
        final_answer = get_final_answer(tracer, user_request, solved_questions, client)

        span.set_output(final_answer)
        span.set_status(StatusCode.OK)
    return final_answer


def decompose_question(tracer, user_request, process_data, client):
    with tracer.start_as_current_span(
        "Decompose", openinference_span_kind="chain"
    ) as span:
        span.set_input(f"decompose user request: {user_request}")
        prompt = DECOMPOSITION_PROMPT.format(
            process_data=process_data, user_request=user_request
        )
        subquestions = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": prompt}],
            response_model=Iterable[SubQuestion],
        )
        span.set_output(subquestions)
        span.set_status(StatusCode.OK)

    return subquestions


def solve_subquestions(tracer, subquestions, user_request, process_data, client):
    with tracer.start_as_current_span("Solve", openinference_span_kind="chain") as span:
        solved_questions = []
        for subquestion in subquestions:
            solved_questions.append(
                SubQuestionWithAnswer(
                    question=subquestion.question,
                    answer=solve(
                        subquestion.question,
                        solved_questions,
                        user_request,
                        process_data,
                        client,
                    ),
                )
            )
        span.set_output(solved_questions)
        span.set_status(StatusCode.OK)

    return solved_questions


def get_final_answer(tracer, user_request, solved_questions, client):

    with tracer.start_as_current_span(
        "Final Answer", openinference_span_kind="chain"
    ) as span:
        span.set_input(
            f"final answer for user request: {user_request}, solved questions: {solved_questions}"
        )
        prompt = FINAL_ANSWER_PROMPT.format(
            solved_questions=solved_questions, user_request=user_request
        )
        final_answer = client.chat.completions.create(
            model=MODEL,
            response_model=ProcessResponse,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )
        span.set_output(final_answer)
        span.set_status(StatusCode.OK)
    return final_answer


def solve(question, solved_questions, original_question, process_data, client):
    prompt = SOLVE_SUBQUESTION_PROMPT.format(process_data=process_data, original_question=original_question, solved_questions=solved_questions, question=question)
    return client.chat.completions.create(
        model=MODEL,
        response_model=SubQuestionWithAnswer,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    ).answer


if __name__ == "__main__":

    # Starting the tracer
    tracer = init_phoenix("llm-process-extraction-decomposition")

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("BASE_URL"))
    client = instructor.from_openai(client, mode=instructor.Mode.JSON)

    requests = pd.read_csv("local_data/requests.csv", header=0)
    # Iterate over every request stored in local_data/requests.csv
    # The folder "local_data" and its contents have to be created manually before running this file
    for i, row in requests.iterrows():

        user_request = row["user_request"]
        data = open("local_data/" + row["data_file"], encoding="utf-8")
        process_data = data.read()

        decompose_ask_about_process(tracer, user_request, process_data, client)
