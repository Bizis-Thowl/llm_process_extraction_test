SOLVE_SUBQUESTION_PROMPT = """
            <Prozess-Modellierung>
            {process_data}
            </Prozess-Modellierung>
            
            <Original-Frage>
            {original_question}
            </Original-Frage>

            <gelöste-Unterfragen>
            {solved_questions}
            </gelöste-Unterfragen>

            Löse diese nächste Unterfrage: {question}
            """
