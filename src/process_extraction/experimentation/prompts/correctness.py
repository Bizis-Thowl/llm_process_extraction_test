CORRECTNESS_PROMPT = """
    Du bist ein Experte für die Korrektheit von Antworten.
    
    Die Fragestellung ist folgende: {user_request}
    
    Die korrekte Antwort ist folgende: {correct_answer}
    
    Die generierte Antwort ist folgende: {generated_answer}
    
    Bewerte die Korrektheit der generierten Antwort.
"""