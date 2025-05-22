import os
from typing import Type, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from crewai import Agent, Task, LLM  # Wird benötigt, um dynamisch einen Summarizer-Agenten zu erstellen

# Umgebungsvariablen für den Fall laden, dass wir ein eigenes LLM erstellen müssen
from dotenv import load_dotenv
load_dotenv()

# Versuche, das default_llm aus agents.py zu importieren - mit verbesserter Circular Import Behandlung
default_llm = None
try:
    # Verzögerter Import um Circular Import Probleme zu vermeiden
    import sys
    if 'agents' in sys.modules:
        # agents.py ist bereits geladen
        from agents import default_llm
        print("--- Debug (TextSummarizationTool): default_llm erfolgreich aus bereits geladenem agents.py importiert ---")
    else:
        # Erster Import - kann zu Circular Import führen, daher vorsichtig
        try:
            from agents import default_llm
            print("--- Debug (TextSummarizationTool): default_llm erfolgreich aus agents.py importiert ---")
        except ValueError as ve:
            # Dies fängt den "LITELLM_MODEL_NAME not found" Fehler ab
            print(f"WARNUNG (TextSummarizationTool): Fehler beim Laden von agents.py: {ve}")
            default_llm = None
        except ImportError as ie:
            # Circular Import oder anderer Import-Fehler
            print(f"WARNUNG (TextSummarizationTool): Import-Fehler beim Laden von agents.py: {ie}")
            default_llm = None
except Exception as e:
    default_llm = None
    print(f"WARNUNG (TextSummarizationTool): Unerwarteter Fehler beim Importieren von default_llm: {e}")

# Globale Variable für den Summarizer Agenten, um ihn nicht bei jedem Aufruf neu zu erstellen
_summarizer_agent: Optional[Agent] = None

def get_summarizer_agent() -> Optional[Agent]:
    """
    Erstellt oder gibt den globalen Summarizer-Agenten zurück.
    Verwendet das default_llm, das in agents.py konfiguriert wurde.
    Falls dies nicht verfügbar ist, wird versucht, ein eigenes LLM zu erstellen.
    """
    global _summarizer_agent
    if _summarizer_agent is None:
        llm_to_use = None
        if default_llm is None:
            # Versuche erneut, das LLM zu laden, falls es beim ersten Mal nicht verfügbar war
            try:
                from agents import default_llm as reloaded_llm
                if reloaded_llm is None:
                    print("TOOL_ERROR (TextSummarizationTool): default_llm ist immer noch None nach erneutem Laden.")
                    
                    # Wir versuchen, ein eigenes LLM zu erstellen als Fallback
                    gemini_api_key = os.getenv("GEMINI_API_KEY")
                    lite_llm_model_name = os.getenv("LITELLM_MODEL_NAME")
                    
                    if not gemini_api_key:
                        print("TOOL_ERROR (TextSummarizationTool): GEMINI_API_KEY nicht in Umgebungsvariablen gefunden.")
                        if lite_llm_model_name:
                            print(f"TOOL_ERROR (TextSummarizationTool): LITELLM_MODEL_NAME ist auf '{lite_llm_model_name}' gesetzt.")
                        else:
                            print("TOOL_ERROR (TextSummarizationTool): LITELLM_MODEL_NAME fehlt in Umgebungsvariablen.")
                            # Setzen wir einen Standard-Wert, damit wir weitermachen können
                            lite_llm_model_name = "gemini/gemini-1.5-flash"
                            print(f"TOOL_ERROR (TextSummarizationTool): LITELLM_MODEL_NAME auf Standardwert '{lite_llm_model_name}' gesetzt.")
                        
                        return None
                    
                    if not lite_llm_model_name:
                        # Setzen wir einen Standard-Wert, damit wir weitermachen können
                        lite_llm_model_name = "gemini/gemini-1.5-flash"
                        print(f"TOOL_ERROR (TextSummarizationTool): LITELLM_MODEL_NAME fehlt in Umgebungsvariablen. Verwende Standardwert '{lite_llm_model_name}'.")
                    
                    try:
                        # Erstelle ein eigenes LLM als Fallback
                        print(f"--- Debug (TextSummarizationTool): Erstelle eigenes LLM mit Modell '{lite_llm_model_name}' ---")
                        llm_to_use = LLM(
                            model=lite_llm_model_name,
                            api_key=gemini_api_key
                        )
                        print("--- Debug (TextSummarizationTool): Eigenes LLM erfolgreich erstellt ---")
                    except Exception as llm_error:
                        print(f"TOOL_ERROR (TextSummarizationTool): Fehler beim Erstellen des eigenen LLM: {llm_error}")
                        return None
                else:
                    llm_to_use = reloaded_llm
                    print("--- Debug (TextSummarizationTool): default_llm erfolgreich nachgeladen. ---")
            except ImportError:
                print("TOOL_ERROR (TextSummarizationTool): default_llm konnte auch beim erneuten Versuch nicht importiert werden.")
                
                # Wir versuchen, ein eigenes LLM zu erstellen als Fallback
                gemini_api_key = os.getenv("GEMINI_API_KEY")
                if not gemini_api_key:
                    print("TOOL_ERROR (TextSummarizationTool): GEMINI_API_KEY nicht in Umgebungsvariablen gefunden. Kann Summarizer Agent nicht erstellen.")
                    return None
                
                # Setzen wir einen Standard-Wert für das Modell
                lite_llm_model_name = "gemini/gemini-1.5-flash"
                print(f"TOOL_ERROR (TextSummarizationTool): Verwende Standardwert '{lite_llm_model_name}' für LITELLM_MODEL_NAME")
                
                try:
                    # Erstelle ein eigenes LLM als Fallback
                    print(f"--- Debug (TextSummarizationTool): Erstelle eigenes LLM mit Modell '{lite_llm_model_name}' ---")
                    llm_to_use = LLM(
                        model=lite_llm_model_name,
                        api_key=gemini_api_key
                    )
                    print("--- Debug (TextSummarizationTool): Eigenes LLM erfolgreich erstellt ---")
                except Exception as llm_error:
                    print(f"TOOL_ERROR (TextSummarizationTool): Fehler beim Erstellen des eigenen LLM: {llm_error}")
                    return None
        else:
            llm_to_use = default_llm
            print("--- Debug (TextSummarizationTool): Verwende bereits importiertes default_llm. ---")
        
        if llm_to_use is None:  # Zusätzliche Sicherheitsüberprüfung
             print("TOOL_ERROR (TextSummarizationTool): llm_to_use ist None. Abbruch der Agenten-Erstellung.")
             return None

        try:
            _summarizer_agent = Agent(
                role="Expert Text Summarizer",
                goal="Summarize the given text concisely and accurately, extracting the most important information. "
                     "The summary should be significantly shorter than the original text while retaining key insights.",
                backstory="You are a highly skilled AI assistant specialized in reading and summarizing long texts. "
                          "You are adept at identifying core arguments, key facts, and main themes, "
                          "and presenting them in a brief and easy-to-understand format.",
                llm=llm_to_use,
                verbose=False,  # Kann für Debugging auf True gesetzt werden
                allow_delegation=False
            )
            print("--- Debug (TextSummarizationTool): Summarizer Agent initialized. ---")
        except Exception as e:
            print(f"TOOL_ERROR (TextSummarizationTool): Fehler beim Initialisieren des Summarizer Agent: {e}")
            _summarizer_agent = None  # Sicherstellen, dass es None bleibt bei Fehler
            return None
            
    return _summarizer_agent

class TextSummarizationToolInput(BaseModel):
    """Input schema for TextSummarizationTool."""
    text_to_summarize: str = Field(..., description="The text content that needs to be summarized.")
    max_length: Optional[int] = Field(
        None, 
        description="Optional: Desired maximum length of the summary in words or tokens (model dependent). "
                    "If not provided, the model will choose an appropriate length."
    )
    summary_focus: Optional[str] = Field(
        None,
        description="Optional: Specific aspects or questions the summary should focus on or answer. "
                    "E.g., 'Focus on the financial implications.' or 'What are the main conclusions?'"
    )

class TextSummarizationTool(BaseTool):
    name: str = "Text Summarization Tool"
    description: str = """
    Summarizes a given text using an AI model by delegating to a specialized Summarizer Agent. 
    Useful for condensing long documents, articles, or scraped web content into a shorter, digestible format.
    You can optionally specify a maximum length for the summary and a specific focus.
    """
    args_schema: Type[BaseModel] = TextSummarizationToolInput  # <-- FIXED: Added Type annotation

    def _run(self, text_to_summarize: str, max_length: Optional[int] = None, summary_focus: Optional[str] = None) -> str:
        """
        Summarizes the provided text by creating a task for the specialized Summarizer Agent.
        """
        print(f"--- Debug (Tool Call): 'Text Summarization Tool' called. Text length: {len(text_to_summarize)}, Max length: {max_length}, Focus: {summary_focus} ---")

        # Fehlerbehandlung für leeren Text
        if not text_to_summarize or not isinstance(text_to_summarize, str):
            return "TOOL_ERROR (TextSummarizationTool): 'text_to_summarize' argument must be a non-empty string."

        # Hole oder initialisiere den Summarizer Agenten
        summarizer_agent = get_summarizer_agent()
        if not summarizer_agent:
            return "TOOL_ERROR (TextSummarizationTool): Summarizer agent could not be initialized. Check LLM configuration and 'agents.py' import."

        # Erstelle den Prompt für den Summarizer Agenten
        task_description = f"Please summarize the following text:\n\n---\n{text_to_summarize}\n---\n\n"
        if summary_focus:
            task_description += f"The summary should specifically focus on: {summary_focus}.\n"
        if max_length:
            task_description += f"Aim for a summary of approximately {max_length} words or tokens.\n"
        
        task_description += "Provide only the summary itself, without any introductory phrases like 'Here is the summary:' or any of your own conversational text."

        # Erstelle die Task für den Summarizer Agenten
        summarization_task = Task(
            description=task_description,
            expected_output="A concise and accurate summary of the provided text, adhering to any specified focus or length constraints. The output should be ONLY the summary text.",
            agent=summarizer_agent
        )

        try:
            print(f"--- Debug (TextSummarizationTool): Starting summarization task for Summarizer Agent. Task description preview: '{task_description[:250]}...' ---")
            # Führe die Task aus. Die execute_sync Methode wird hier verwendet, da _run synchron ist.
            task_output = summarization_task.execute_sync() 
            
            # Verarbeitung des TaskOutput-Objekts
            # In neueren Versionen von CrewAI gibt task.execute_sync() ein TaskOutput-Objekt zurück
            # Wir müssen prüfen, welches Attribut wir verwenden sollen
            if hasattr(task_output, 'raw'):
                # Neuere CrewAI-Versionen verwenden das 'raw'-Attribut
                summary = task_output.raw
            elif hasattr(task_output, 'result'):
                # Einige Versionen verwenden das 'result'-Attribut
                summary = task_output.result
            elif hasattr(task_output, 'output'):
                # Andere Versionen könnten das 'output'-Attribut verwenden
                summary = task_output.output
            elif isinstance(task_output, str):
                # Fallback für den Fall, dass ein String zurückgegeben wird
                summary = task_output
            else:
                # Wenn wir nicht wissen, wie wir das Objekt verarbeiten sollen, versuchen wir, es als String zu konvertieren
                summary = str(task_output)
            
            print(f"--- Debug (TextSummarizationTool): Summarization successful. Summary type: {type(summary)}, content: '{summary[:100]}...' ---")
            return summary.strip() if isinstance(summary, str) else str(summary).strip()
        except Exception as e:
            error_msg = f"TOOL_ERROR (TextSummarizationTool): An error occurred during text summarization task execution: {e}"
            print(f"--- Debug (TextSummarizationTool): {error_msg} ---")
            # Versuche, spezifischere Fehler von LiteLLM oder dem LLM-Aufruf zu bekommen, falls möglich
            if hasattr(e, 'message'):  # Typisch für manche Exception-Objekte
                error_msg += f" Details: {e.message}"
            elif hasattr(e, 'args') and e.args:  # Generische Exceptions haben oft Details in args
                error_msg += f" Details: {e.args[0] if e.args else ''}"
            return error_msg

# Instanz des Tools erstellen, damit es von Agenten importiert und verwendet werden kann
text_summarization_tool = TextSummarizationTool()

if __name__ == '__main__':
    """
    Test-Block für das TextSummarizationTool.
    Führt verschiedene Tests durch, um die Funktionalität zu überprüfen.
    """
    print("=== Lokaler Test für TextSummarizationTool ===")
    
    # Sicherstellen, dass .env geladen wurde
    from dotenv import load_dotenv
    load_dotenv()
    
    # Überprüfen, ob die nötigen Umgebungsvariablen gesetzt sind
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    lite_llm_model_name = os.getenv("LITELLM_MODEL_NAME")
    
    if not gemini_api_key:
        print("WARNUNG: GEMINI_API_KEY nicht gefunden. Tests werden nicht funktionieren.")
    else:
        print(f"GEMINI_API_KEY gefunden: {gemini_api_key[:5]}..." if gemini_api_key else "GEMINI_API_KEY fehlt")
    
    if not lite_llm_model_name:
        # Setzen wir einen Standard-Wert für das Modell
        lite_llm_model_name = "gemini/gemini-1.5-flash"
        # Explizit setzen, so dass andere Module es auch sehen können
        os.environ["LITELLM_MODEL_NAME"] = lite_llm_model_name
        print(f"WARNUNG: LITELLM_MODEL_NAME nicht gefunden. Setze Standardwert: {lite_llm_model_name}")
    else:
        print(f"LITELLM_MODEL_NAME: {lite_llm_model_name}")
    
    # Initialisiere den Summarizer Agenten für den Test
    summarizer_agent_instance = get_summarizer_agent()

    if not summarizer_agent_instance:
        print("FEHLER: Summarizer Agent konnte für den Test nicht initialisiert werden. Überprüfe die LLM-Konfiguration und den Import von 'agents.default_llm'.")
    else:
        print("Summarizer Agent für Test erfolgreich initialisiert.")
        
        # Test 1: Kurzer Text ohne Optionen
        example_text_short = "The quick brown fox jumps over the lazy dog. This is a classic pangram used to test typefaces and is often used in design mockups."
        print("\n=== Test 1: Kurzer Text ohne Optionen ===")
        try:
            result_short = text_summarization_tool._run(example_text_short)
            print(f"Zusammenfassung: {result_short}")
        except Exception as e:
            print(f"Test 1 fehlgeschlagen: {e}")
        
        # Test 2: Längerer Text ohne Optionen
        example_text_long = (
            "Artificial intelligence (AI) is intelligence demonstrated by machines, "
            "as opposed to the natural intelligence displayed by humans and animals. "
            "Leading AI textbooks define the field as the study of 'intelligent agents': "
            "any device that perceives its environment and takes actions that maximize its "
            "chance of successfully achieving its goals. Some popular accounts use the term "
            "'artificial intelligence' to describe machines that mimic 'cognitive' functions "
            "that humans associate with the human mind, such as 'learning' and 'problem solving'.\n\n"
            "As machines become increasingly capable, tasks considered to require 'intelligence' "
            "are often removed from the definition of AI, a phenomenon known as the AI effect. "
            "Current AI capabilities include understanding human speech, competing at the highest "
            "level in strategic game systems (such as chess and Go), autonomously operating cars, "
            "creative content generation, and intelligent routing in content delivery networks."
        )
        print("\n=== Test 2: Längerer Text ohne Optionen ===")
        try:
            result_long = text_summarization_tool._run(example_text_long)
            print(f"Zusammenfassung: {result_long}")
        except Exception as e:
            print(f"Test 2 fehlgeschlagen: {e}")
        
        # Weitere Tests werden nur durchgeführt, wenn die ersten Tests erfolgreich waren
        if 'result_long' in locals() and result_long and not result_long.startswith("TOOL_ERROR"):
            # Test 3: Mit max_length Parameter
            print("\n=== Test 3: Mit max_length Parameter ===")
            try:
                result_length = text_summarization_tool._run(example_text_long, max_length=30)
                print(f"Zusammenfassung (max. 30 Wörter): {result_length}")
            except Exception as e:
                print(f"Test 3 fehlgeschlagen: {e}")
            
            # Test 4: Mit summary_focus Parameter
            print("\n=== Test 4: Mit summary_focus Parameter ===")
            try:
                result_focus = text_summarization_tool._run(
                    example_text_long, 
                    summary_focus="Focus on the historical development and changing definition of AI."
                )
                print(f"Zusammenfassung (mit Fokus): {result_focus}")
            except Exception as e:
                print(f"Test 4 fehlgeschlagen: {e}")
            
            # Test 5: Leerer Eingabetext
            print("\n=== Test 5: Leerer Eingabetext ===")
            try:
                result_empty = text_summarization_tool._run("")
                print(f"Ergebnis: {result_empty}")
            except Exception as e:
                print(f"Test 5 fehlgeschlagen: {e}")
            
            # Test 6: Test mit beiden Optionen
            print("\n=== Test 6: Mit beiden Optionen (max_length und summary_focus) ===")
            try:
                result_both = text_summarization_tool._run(
                    example_text_long,
                    max_length=25,
                    summary_focus="Focus on practical applications of AI."
                )
                print(f"Zusammenfassung (max. 25 Wörter, Fokus auf Anwendungen): {result_both}")
            except Exception as e:
                print(f"Test 6 fehlgeschlagen: {e}")
        else:
            print("\nÜberspringe weitere Tests, da die grundlegenden Tests fehlgeschlagen sind.")
            
    print("\n=== Tests abgeschlossen ===")