FINAL_ANSWER_PROMPT = """
                Du sollst eine Frage zu einem Prozess beantworten.
                
                Hierzu hast du dir bereits Gedanken gemacht und eine Liste an unterfragen erstellt und beantwortet:
                
                {solved_questions}

                Beantworte die folgende Useranfrage:

                {user_request}

                Bei Beantwortung der Useranfrage, beschreibe den Prozess, sodass ihn jemand versteht, der:die die Modellierung nicht vorliegen hat.
                """
