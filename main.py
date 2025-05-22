import os
import json
from dotenv import load_dotenv
from crewai import Task, Crew, Process
import time 

# Load environment variables FIRST
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY nicht in .env gefunden! Bitte in der .env Datei eintragen.")

os.environ["GEMINI_API_KEY"] = gemini_api_key
# GOOGLE_API_KEY wird oft von LangChain oder anderen Google-Bibliotheken intern verwendet,
# daher ist es gut, ihn auch zu setzen, oft ist er identisch mit dem GEMINI_API_KEY für Gemini-Modelle.
os.environ["GOOGLE_API_KEY"] = gemini_api_key 

lite_llm_model_name = os.getenv("LITELLM_MODEL_NAME", "gemini/gemini-1.5-flash")
os.environ["LITELLM_MODEL_NAME"] = lite_llm_model_name

serper_api_key = os.getenv("SERPER_API_KEY")
if serper_api_key:
    os.environ["SERPER_API_KEY"] = serper_api_key
else:
    print("WARNUNG: SERPER_API_KEY nicht in .env gefunden!")

from agents import project_manager_agent, developer_agent, researcher_agent, tester_agent, debug_agent
from tools.web_tools import close_browser_tool
from tools.server_tools import stop_local_http_server_tool, is_port_available 

# --- Pfaddefinitionen ---
# Basis-Projektpfad für Artefakte und generierten Code
script_dir = os.path.dirname(__file__)
base_project_path = os.path.join(script_dir, "test_project_vision_tool") # Eigener Ordner für diesen Test
artifacts_path = os.path.join(base_project_path, "agent_artifacts")
application_code_path = os.path.join(base_project_path, "application_code") 

# Pfad zum Testbild (angenommen im Projekt-Root/test_images)
test_image_for_pm_analysis = os.path.join(script_dir, "test_images", "test_mockup.png") 
pm_vision_analysis_report_file = os.path.join(artifacts_path, "pm_vision_analysis_report.md")

# Pfade für den Text Summarization Test
text_summarization_test_dir = os.path.join(script_dir, "test_text_summarization")
input_text_file = os.path.join(text_summarization_test_dir, "input_text.txt")
summary_output_file = os.path.join(text_summarization_test_dir, "summary_output.md")
researcher_summary_file = os.path.join(text_summarization_test_dir, "researcher_summary.md")

# Beispieltext für den Summarization Test
EXAMPLE_TEXT = """
Artificial Intelligence (AI) and Machine Learning (ML) are transforming industries across the globe. 
AI refers to machines or software that can perform tasks that typically require human intelligence, 
such as visual perception, speech recognition, decision-making, and language translation. 
Machine Learning, a subset of AI, enables systems to learn from data and improve their performance 
over time without being explicitly programmed.

The history of AI dates back to the 1950s when the term was first coined. Early AI research 
focused on symbolic approaches, logical reasoning, and expert systems. However, progress was 
limited by computational power and the availability of data. The AI winter in the 1970s and 
1980s was characterized by reduced funding and interest in AI research due to unmet expectations.

The resurgence of AI in the 21st century can be attributed to three key factors: the explosion 
of digital data, advancements in computational power, and breakthroughs in machine learning 
algorithms, particularly neural networks and deep learning. Today, AI applications range from 
virtual assistants like Siri and Alexa to recommendation systems on streaming platforms, 
autonomous vehicles, medical diagnosis tools, and more.

Deep learning, a subset of machine learning, has been particularly successful in recent years. 
Deep learning models use neural networks with many layers (hence "deep") to analyze data. These 
models have achieved remarkable results in image and speech recognition, natural language 
processing, and game playing, among other tasks.

Despite the progress, AI faces several challenges. Ethical considerations include privacy 
concerns, bias in AI algorithms, job displacement due to automation, and the potential for 
autonomous weapons. Technical challenges include the need for vast amounts of high-quality 
data, the "black box" nature of many AI systems making them difficult to interpret, and the 
energy consumption of training large models.

The future of AI holds significant promise. Research areas such as explainable AI aim to make 
AI systems more transparent and interpretable. Reinforcement learning, where agents learn by 
interacting with an environment, has shown promise in areas such as robotics and game playing. 
Federated learning allows models to be trained across multiple decentralized devices holding 
local data samples without exchanging them, addressing privacy concerns.

As AI continues to evolve, interdisciplinary collaboration between computer scientists, 
ethicists, policymakers, and domain experts will be crucial to ensure that AI development 
benefits humanity while minimizing risks. The alignment of AI systems with human values and 
the establishment of regulatory frameworks will be important areas of focus.

The field of AI is still in its early stages compared to its potential, and the coming decades 
will likely see even more transformative applications as research continues and technology advances.
"""

# --- Task für den Vision Tool Test ---
task_pm_analyze_mockup = Task(
    description=(
        f"You are the Project Manager. Your task is to analyze a UI mockup image. "
        f"The image is located at the path: '{test_image_for_pm_analysis}'.\n"
        f"1. Use the 'Gemini Vision Analyzer Tool' to analyze this image.\n"
        f"2. For the analysis prompt, use the following: 'Thoroughly describe all UI elements visible in this mockup. "
        f"Identify the overall layout, color scheme, typography, and any interactive elements suggested by the design. "
        f"Extract any visible text content. Note the perceived style or branding.'\n"
        f"3. After receiving the analysis, write a comprehensive report based on the analysis text. "
        f"The report should summarize the findings clearly.\n"
        f"4. Save this report to the file: '{pm_vision_analysis_report_file}' using the 'Write File Tool'."
    ),
    expected_output=(
        f"A confirmation that the UI mockup analysis has been completed and the detailed report "
        f"has been successfully written to '{pm_vision_analysis_report_file}'. "
        f"Include the full content of the written report in your final output."
    ),
    agent=project_manager_agent,
)

vision_test_crew = Crew(
    agents=[project_manager_agent],
    tasks=[task_pm_analyze_mockup],
    process=Process.sequential,
    verbose=True
)

# --- NEUE TASKS UND CREW FÜR TEXT SUMMARIZATION TOOL TEST ---

# Task für Project Manager, um Text mit dem Text Summarization Tool zusammenzufassen
task_pm_summarize_text = Task(
    description=(
        f"You are the Project Manager. Your task is to summarize a long text document.\n"
        f"1. First, create the input text file at: '{input_text_file}' with the following content:\n'''{EXAMPLE_TEXT}'''\n"
        f"2. Then, read this file to get the text content.\n"
        f"3. Use the 'Text Summarization Tool' to create a concise summary of this text.\n"
        f"4. The summary should focus on the key developments in AI, its main challenges, and future directions.\n"
        f"5. Aim for a summary of approximately 150 words.\n"
        f"6. Save the final summary to: '{summary_output_file}'.\n"
        f"7. Include your thoughts on how effective the 'Text Summarization Tool' was for this task."
    ),
    expected_output=(
        f"A confirmation that the text has been summarized successfully and the summary has been saved to "
        f"'{summary_output_file}'. Include the full content of the summary and your evaluation of the tool."
    ),
    agent=project_manager_agent,
)

# Task für Researcher, um dieselbe Zusammenfassung zu erstellen (um verschiedene Agenten zu testen)
task_researcher_summarize_text = Task(
    description=(
        f"You are the Research Specialist. Your task is to create a research summary of an AI overview text.\n"
        f"1. Read the input text file from: '{input_text_file}'.\n"
        f"2. Use the 'Text Summarization Tool' to analyze and summarize this document.\n"
        f"3. For the summary focus, concentrate on 'historical developments of AI and future research directions'.\n"
        f"4. Aim for a summary of approximately 120 words.\n"
        f"5. Add a section at the end titled 'Research Implications' where you outline 3-4 key implications for AI research.\n"
        f"6. Save your final research summary to: '{researcher_summary_file}'.\n"
        f"7. Provide your professional assessment of how well the summarization tool performed for research purposes."
    ),
    expected_output=(
        f"A confirmation that you've created a research summary using the summarization tool and saved it to "
        f"'{researcher_summary_file}'. Include the full content of your summary and your assessment of the tool's effectiveness for research."
    ),
    agent=researcher_agent,
)

summarization_test_crew = Crew(
    agents=[project_manager_agent, researcher_agent],
    tasks=[task_pm_summarize_text, task_researcher_summarize_text],
    process=Process.sequential,
    verbose=True
)

# --- Ende: NEUE TASKS UND CREW FÜR TEXT SUMMARIZATION TOOL TEST ---

def setup_test_environment(base_path, artifacts_subpath, app_code_subpath):
    """Stellt sicher, dass die Basisverzeichnisse für Tests existieren."""
    os.makedirs(artifacts_subpath, exist_ok=True)
    os.makedirs(app_code_subpath, exist_ok=True) 
    print(f"Basis-Verzeichnisse für Test '{base_path}' sichergestellt/erstellt.")

def run_vision_test():
    # Setup für die Vision-Test-Crew
    setup_test_environment(base_project_path, artifacts_path, application_code_path)

    print(f"\n--- Starte Vision Test Crew ---")
    print(f"Project Manager soll Bild analysieren: '{test_image_for_pm_analysis}'")
    print(f"Analysebericht erwartet in: '{pm_vision_analysis_report_file}'")

    # Überprüfen, ob das Testbild existiert, bevor die Crew gestartet wird
    if not os.path.exists(test_image_for_pm_analysis):
        print(f"FEHLER: Das Testbild '{test_image_for_pm_analysis}' wurde nicht gefunden!")
        print("Bitte stelle sicher, dass das Bild im Ordner 'test_images' im Projekt-Root liegt oder passe den Pfad an.")
        return

    try:
        vision_result = vision_test_crew.kickoff()
        print("\n\n########################")
        print("## Ergebnis der Vision Test Crew:")
        print(vision_result)
        print("########################")

        if os.path.exists(pm_vision_analysis_report_file):
            print(f"\n--- Inhalt des Analyseberichts ({pm_vision_analysis_report_file}): ---")
            with open(pm_vision_analysis_report_file, "r", encoding="utf-8") as f:
                print(f.read())
        else:
            print(f"FEHLER: Der Analysebericht '{pm_vision_analysis_report_file}' wurde nicht erstellt.")

    except Exception as e:
        print(f"\nEin Fehler ist während der Ausführung der Vision Test Crew aufgetreten: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n--- Vision Test Crew abgeschlossen. ---")

def run_summarization_test():
    """Führt den Test für das Text Summarization Tool durch."""
    # Stellt sicher, dass das Verzeichnis für den Summarization-Test existiert
    os.makedirs(text_summarization_test_dir, exist_ok=True)
    
    print(f"\n--- Starte Text Summarization Test Crew ---")
    print(f"Input-Text wird erstellt in: '{input_text_file}'")
    print(f"Erwartete Ausgaben in: '{summary_output_file}' und '{researcher_summary_file}'")
    
    try:
        summarization_result = summarization_test_crew.kickoff()
        print("\n\n########################")
        print("## Ergebnis der Text Summarization Test Crew:")
        print(summarization_result)
        print("########################")
        
        # Prüfe ob die Ausgabedateien erstellt wurden und zeige deren Inhalt an
        for file_path, file_desc in [
            (summary_output_file, "Project Manager Zusammenfassung"),
            (researcher_summary_file, "Researcher Zusammenfassung")
        ]:
            if os.path.exists(file_path):
                print(f"\n--- Inhalt der {file_desc} ({file_path}): ---")
                with open(file_path, "r", encoding="utf-8") as f:
                    print(f.read())
            else:
                print(f"FEHLER: Die {file_desc} '{file_path}' wurde nicht erstellt.")
                
    except Exception as e:
        print(f"\nEin Fehler ist während der Ausführung der Text Summarization Test Crew aufgetreten: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n--- Text Summarization Test Crew abgeschlossen. ---")

if __name__ == '__main__':
    print("Starte IMAP Agent System...")
    
    # Wähle den Test aus, den du ausführen möchtest
    # Setze run_vision_test_flag auf True, um den Vision-Test zu starten
    # Setze run_summarization_test_flag auf True, um den Summarization-Test zu starten
    run_vision_test_flag = False  # Auf True setzen, um den Vision-Test auszuführen
    run_summarization_test_flag = True  # Auf True setzen, um den Summarization-Test auszuführen
    
    if run_vision_test_flag:
        run_vision_test()
    
    if run_summarization_test_flag:
        run_summarization_test()
        
    print("\n--- Alle Testläufe abgeschlossen. ---")