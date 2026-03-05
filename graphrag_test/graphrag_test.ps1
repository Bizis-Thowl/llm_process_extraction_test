# This is a comment
$message = "Graph-RAG test script"
Write-Host $message
#Write-Host "Going into the python venv"
# Invoke-Expression c:\Users\qq6-xd4\Documents\Programmierung\llm_process_extraction_test\llm_process_extraction_test\.venv\Scripts\Activate.ps1
Add-Content -Path .\log.txt -Value "----------------------------------------------------------------------------------------"
Add-Content -Path .\log.txt -Value "Frage 1: Wie heißt dieser Prozess?"
$result = graphrag query \"Wie heißt dieser Prozess?"\ -m local
Write-Host $result
Add-Content -Path .\log.txt -Value $result
Add-Content -Path .\log.txt -Value "----------------------------------------------------------------------------------------"
Add-Content -Path .\log.txt -Value "Frage 2: Wenn ich mich gerade vor einer Dienstreise befinde, was gilt dann für mich zu beachten?" 
$result = graphrag query \"Wenn ich mich gerade vor einer Dienstreise befinde, was gilt dann für mich zu beachten?"\ -m local
Write-Host $result
Add-Content -Path .\log.txt -Value $result
Add-Content -Path .\log.txt -Value "----------------------------------------------------------------------------------------"
Add-Content -Path .\log.txt -Value "Frage 3: Welcher Schritt kommt direkt nach 'Dienstreise antreten' und wer führt ihn aus?" 
$result = graphrag query \"Welcher Schritt kommt direkt nach 'Dienstreise antreten' und wer führt ihn aus?"\ -m local
Write-Host $result
Add-Content -Path .\log.txt -Value $result
Add-Content -Path .\log.txt -Value "----------------------------------------------------------------------------------------"
Add-Content -Path .\log.txt -Value "Frage 4: Welche Dokumente spielen im laufe des Prozesses eine Rolle und für wen?" 
$result = graphrag query \"Welche Dokumente spielen im laufe des Prozesses eine Rolle und für wen?"\ -m local
Write-Host $result
Add-Content -Path .\log.txt -Value $result
Add-Content -Path .\log.txt -Value "----------------------------------------------------------------------------------------"