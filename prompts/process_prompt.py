PROCESS_PROMPT = """
Du sollst Fragen zu einem Prozess beantworten, der im Folgenden vorliegt:

{process_data}

Bei Beantwortung der Useranfrage, beschreibe den Prozess, sodass ihn jemand versteht, der:die die Modellierung nicht vorliegen hat.
Das ist die Useranfrage:

{user_request}
"""