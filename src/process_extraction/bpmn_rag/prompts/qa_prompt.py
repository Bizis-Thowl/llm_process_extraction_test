# Prompts from https://github.com/hoerb1337/LLMmodel2text 
# Translated into German with the help of deepl.com

QA_SYSTEM_PROMPT = """Sie sind ein Experten-Frage&Antwort-System mit Fachwissen zur Geschäftsprozessmodellierungssprache BPMN. Nehmen Sie die Standard-Spezifikation BPMN 2.0.2 zur Hand. Nehmen wir an, Sie haben ein BPMN-Modell erstellt. Nun möchten Sie Nutzern, die keine Kenntnisse der BPMN-Notation haben, Fragen, die diese zu den Prozessen haben, beantworten. Bitte antworten sie in kurzen präzisen Antworten auf Deutsch."""

QA_MESSAGES_PROMPT = """
    Bitte erstellen Sie eine textuelle Prozessbeschreibung für das angegebene, in XML serialisierte BPMN-Modell. Fügen Sie zu jedem im BPMN-Modell verwendeten BPMN-Elementtyp eine kurze Erläuterung der Semantik dieses Elementtyps hinzu.

    Beispielhafte textuelle Prozessbeschreibung für das BPMN-Modell „Example“: {context_str}

    BPMN-Modell „Explain“, serialisiert in XML:
    {explain_str}

    Frage, die mithilfe des BPMN-Modells beantwortet werden soll:
    {query_str}

    """

QA_REFINE_PROMPT = """
    Bitte erstellen Sie eine textuelle Prozessbeschreibung für das angegebene, in XML serialisierte BPMN-Modell. Fügen Sie zu jedem im BPMN-Modell verwendeten BPMN-Elementtyp eine kurze Erläuterung der Semantik dieses Elementtyps hinzu.

    Beispielhafte textuelle Prozessbeschreibung für das BPMN-Modell „Example“: {context_str}

    BPMN-Modell „Explain“, serialisiert in XML:
    {explain_str}

    Frage, die mithilfe des BPMN-Modells beantwortet werden soll:
    {query_str}
    
    Ursprüngliche Antwort auf die Frage über das BPMN-Modell „Explain“: {existing_answer}

    Angepasste textuelle Prozessbeschreibung für das BPMN-Modell „Explain“:
    """