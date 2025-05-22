import os
from typing import Dict, Optional, List, Type
# BaseTool für stabilere Implementierung verwenden
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

# Imports für Google Generative AI (Gemini)
try:
    import google.generativeai as genai
    from PIL import Image
    import requests
    from io import BytesIO
except ImportError:
    print("Hinweis: Für das GeminiVisionAnalyzerTool werden 'google-generativeai', 'Pillow' und 'requests' benötigt. Bitte installieren: pip install google-generativeai Pillow requests")
    # Erlaube dem Rest des Systems zu laden, auch wenn diese fehlen. Das Tool wird dann nicht funktionieren.
    genai = None 
    Image = None
    requests = None
    BytesIO = None


# Globale Variable, um den Gemini Client zu halten, damit er nicht bei jedem Tool-Aufruf neu initialisiert wird.
_gemini_vision_model = None

def ensure_gemini_vision_model():
    """
    Ensures the Gemini Vision model is initialized.
    This should be called before using the model.
    It relies on GEMINI_API_KEY being set in the environment.
    """
    global _gemini_vision_model
    if not genai: # Überprüfen, ob der Import erfolgreich war
        return False

    if _gemini_vision_model is None:
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            print("TOOL_ERROR (GeminiVision): GEMINI_API_KEY not found in environment variables.")
            return False
        try:
            genai.configure(api_key=gemini_api_key)
            _gemini_vision_model = genai.GenerativeModel('gemini-1.5-flash-latest')
            print("--- Debug (GeminiVision): Gemini Vision Model 'gemini-1.5-flash-latest' initialized. ---")
            return True
        except Exception as e:
            print(f"TOOL_ERROR (GeminiVision): Could not initialize Gemini Vision model: {e}")
            _gemini_vision_model = None # Sicherstellen, dass es None bleibt bei Fehler
            return False
    return True


class GeminiVisionAnalyzerToolLogic:
    def _load_image_from_path_or_url(self, image_source: str) -> Optional[Image.Image]:
        """
        Loads an image from a local file path or a URL.
        """
        if not Image or not requests or not BytesIO: # Überprüfen, ob die Importe erfolgreich waren
            print("TOOL_ERROR (GeminiVision): Pillow or requests library not available.")
            return None
        try:
            if image_source.startswith(('http://', 'https://')):
                print(f"--- Debug (GeminiVision): Loading image from URL: {image_source} ---")
                response = requests.get(image_source, stream=True, timeout=20)
                response.raise_for_status()
                img = Image.open(BytesIO(response.content))
                print(f"--- Debug (GeminiVision): Image loaded successfully from URL. Format: {img.format}, Mode: {img.mode}, Size: {img.size} ---")
                return img
            elif os.path.exists(image_source):
                print(f"--- Debug (GeminiVision): Loading image from local path: {image_source} ---")
                img = Image.open(image_source)
                print(f"--- Debug (GeminiVision): Image loaded successfully from path. Format: {img.format}, Mode: {img.mode}, Size: {img.size} ---")
                return img
            else:
                print(f"--- Debug (GeminiVision): Image source '{image_source}' is not a valid URL or local file path. ---")
                return None
        except requests.exceptions.RequestException as e:
            print(f"--- Debug (GeminiVision): Error loading image from URL '{image_source}': {e} ---")
            return None
        except FileNotFoundError:
            print(f"--- Debug (GeminiVision): Image file not found at path '{image_source}'. ---")
            return None
        except IOError as e: # Deckt Probleme mit dem Öffnen/Lesen des Bildes ab
            print(f"--- Debug (GeminiVision): Error opening or reading image '{image_source}': {e} ---")
            return None
        except Exception as e:
            print(f"--- Debug (GeminiVision): Unexpected error loading image '{image_source}': {e} ---")
            return None

    def analyze_image(self, image_path_or_url: str, prompt: str, max_output_tokens: int = 2048) -> Dict[str, Optional[str]]:
        """
        Analyzes an image using the Gemini Vision model with a specific prompt.

        Args:
            image_path_or_url (str): The local file path or URL of the image to analyze.
            prompt (str): The prompt to guide the vision model's analysis.
            max_output_tokens (int): The maximum number of tokens for the response.

        Returns:
            Dict[str, Optional[str]]: A dictionary containing:
                'analysis_text': The textual analysis from the model, or None on error.
                'error': An error message if the analysis failed, or None on success.
        """
        global _gemini_vision_model
        result = {"analysis_text": None, "error": None}

        if not genai: # Überprüfen, ob der Import erfolgreich war
            result["error"] = "TOOL_ERROR (GeminiVision): 'google-generativeai' library is not installed or failed to import."
            return result

        if not ensure_gemini_vision_model() or _gemini_vision_model is None:
            result["error"] = "TOOL_ERROR (GeminiVision): Gemini Vision model is not initialized. Check API key and dependencies."
            return result

        pil_image = self._load_image_from_path_or_url(image_path_or_url)
        if pil_image is None:
            result["error"] = f"TOOL_ERROR (GeminiVision): Could not load image from '{image_path_or_url}'."
            return result

        try:
            print(f"--- Debug (GeminiVision): Sending image and prompt to Gemini Vision model. Prompt: '{prompt[:100]}...' ---")
            # Die GenerationConfig wird direkt in generate_content verwendet oder global gesetzt
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_output_tokens
            )
            response = _gemini_vision_model.generate_content(
                contents=[prompt, pil_image], # Die Reihenfolge [Text, Bild] ist wichtig
                generation_config=generation_config,
                stream=False # Für dieses Tool ist kein Streaming notwendig
            )
            
            # Zugriff auf den Text der Antwort
            if response.candidates and response.candidates[0].content.parts:
                analysis_text = "".join(part.text for part in response.candidates[0].content.parts if hasattr(part, 'text'))
                result["analysis_text"] = analysis_text.strip()
                print(f"--- Debug (GeminiVision): Analysis successful. Output length: {len(result['analysis_text'])} ---")
            else:
                # Versuche, genauere Fehlerinformationen zu bekommen, falls vorhanden
                error_detail = "No content in response or unexpected response structure."
                if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                    error_detail = f"Content blocked. Reason: {response.prompt_feedback.block_reason_message or response.prompt_feedback.block_reason}"
                elif not response.candidates:
                    error_detail = "No candidates returned in the response."
                
                result["error"] = f"TOOL_ERROR (GeminiVision): {error_detail}"
                print(f"--- Debug (GeminiVision): {result['error']} ---")

        except Exception as e:
            error_msg = f"TOOL_ERROR (GeminiVision): An unexpected error occurred during analysis: {e}"
            print(f"--- Debug (GeminiVision): {error_msg} ---")
            result["error"] = error_msg
        
        return result

_vision_analyzer_logic = GeminiVisionAnalyzerToolLogic()

# Definieren der Input-Schema-Klasse für das Tool
class GeminiVisionAnalyzerInput(BaseModel):
    """Input schema für GeminiVisionAnalyzerTool."""
    image_path_or_url: str = Field(
        ..., 
        description="Der lokale Dateipfad oder eine öffentlich zugängliche URL des zu analysierenden Bildes."
    )
    prompt: str = Field(
        ..., 
        description="Der detaillierte Text-Prompt zur Steuerung der Vision-Modellanalyse."
    )
    max_output_tokens: int = Field(
        2048, 
        description="Die maximale Anzahl von Tokens für die Antwort. Standard ist 2048."
    )

# BaseTool-Implementierung für den Gemini Vision Analyzer
class GeminiVisionAnalyzerTool(BaseTool):
    name: str = "Gemini Vision Analyzer Tool"
    description: str = """
    Analysiert ein Bild (von einem lokalen Pfad oder einer URL) mit Google's Gemini Vision-Modell und einem spezifischen Text-Prompt.
    Dieses Tool ist nützlich, um den Inhalt von Design-Mockups zu verstehen, UI-Elemente zu identifizieren,
    Farben, Layout-Strukturen oder andere visuelle Aspekte, die im Prompt beschrieben sind.
    """
    args_schema: Type[BaseModel] = GeminiVisionAnalyzerInput
    
    def _run(self, image_path_or_url: str, prompt: str, max_output_tokens: int = 2048) -> str:
        """
        Führt die Analyse des Bildes durch und gibt das Ergebnis zurück.
        """
        print(f"--- Debug (Tool Call): 'Gemini Vision Analyzer Tool' called with image: '{image_path_or_url}', prompt: '{prompt[:100]}...' ---")
        
        if not image_path_or_url or not isinstance(image_path_or_url, str):
            return "TOOL_ERROR (GeminiVision): 'image_path_or_url' argument must be a non-empty string."
        if not prompt or not isinstance(prompt, str):
            return "TOOL_ERROR (GeminiVision): 'prompt' argument must be a non-empty string."
        if not isinstance(max_output_tokens, int) or max_output_tokens <= 0:
            return "TOOL_ERROR (GeminiVision): 'max_output_tokens' must be a positive integer."

        analysis_result = _vision_analyzer_logic.analyze_image(image_path_or_url, prompt, max_output_tokens)

        if analysis_result["error"]:
            return analysis_result["error"]
        elif analysis_result["analysis_text"] is not None:
            return analysis_result["analysis_text"]
        else:
            # Fallback, sollte eigentlich durch vorherige Checks abgedeckt sein
            return "TOOL_ERROR (GeminiVision): Analysis failed for an unknown reason or returned empty."

# Instanz des Tools erstellen, damit es von Agenten importiert und verwendet werden kann
gemini_vision_analyzer_tool = GeminiVisionAnalyzerTool()

if __name__ == '__main__':
    # --- Setup für lokales Testen (ähnlich wie in agents.py) ---
    print("--- Lokaler Test für GeminiVisionAnalyzerTool ---")
    
    from dotenv import load_dotenv
    load_dotenv()

    gemini_api_key_exists = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key_exists:
        print("FEHLER: GEMINI_API_KEY nicht in den Umgebungsvariablen gefunden. Bitte setzen Sie sie.")
    else:
        print("GEMINI_API_KEY gefunden.")
        
        if not ensure_gemini_vision_model():
            print("Modellinitialisierung fehlgeschlagen. Tests können nicht durchgeführt werden.")
        else:
            print("Gemini Vision Modell erfolgreich initialisiert für den Test.")
            
            # Testfälle - Direktes Aufrufen der _run-Methode zum Testen
            print("\n--- Testfall 1: Nicht existierende lokale Datei ---")
            # Die Instanz heißt gemini_vision_analyzer_tool
            result1 = gemini_vision_analyzer_tool._run(
                image_path_or_url="path/to/non_existent_mockup.jpg",
                prompt="Describe this image.",
                max_output_tokens=50
            )
            print(f"Ergebnis 1: {result1}")
            assert "TOOL_ERROR" in result1
            
            test_image_url_png = "https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png"

            print(f"\n--- Testfall 2: Öffentliche Bild-URL ({test_image_url_png}) ---")
            result2 = gemini_vision_analyzer_tool._run(
                image_path_or_url=test_image_url_png,
                prompt="What is shown in this image? Be concise.",
                max_output_tokens=100
            )
            print(f"Ergebnis 2: {result2}")

            print("\n--- Testfall 3: Ungültiger Prompt ---")
            result3 = gemini_vision_analyzer_tool._run(
                image_path_or_url=test_image_url_png,
                prompt="" 
            )
            print(f"Ergebnis 3: {result3}")
            assert "TOOL_ERROR" in result3

            print("\n--- Testfall 4: Ungültige Bild-URL ---")
            result4 = gemini_vision_analyzer_tool._run(
                image_path_or_url="http://invalid.url/image.png",
                prompt="Describe this image.",
                max_output_tokens=50
            )
            print(f"Ergebnis 4: {result4}")
            assert "TOOL_ERROR" in result4

            # Korrekter Pfad relativ zum Projektverzeichnis, wenn das Skript im tools-Ordner ist
            # und test_images auf derselben Ebene wie tools liegt.
            # Für den direkten Aufruf von "python tools/vision_analyzer_tool.py" muss der Pfad
            # relativ zum tools-Ordner sein, also ".." um eine Ebene höher zu gelangen.
            # Besser: Relativ zum Skript selbst machen
            script_dir = os.path.dirname(__file__) # Verzeichnis des aktuellen Skripts
            # Wenn test_images im Projekt-Root liegt (eine Ebene über tools/)
            local_test_image_path_project_root = os.path.join(script_dir, "..", "test_images", "test_mockup.png")
            # Wenn test_images direkt im tools-Ordner wäre (weniger wahrscheinlich)
            # local_test_image_path_tools_dir = os.path.join(script_dir, "test_images", "test_mockup.png")

            # Wir gehen davon aus, dass test_images im Projekt-Root ist
            local_test_image_path = local_test_image_path_project_root
            
            if os.path.exists(local_test_image_path):
                print(f"\n--- Testfall 5: Lokales Testbild ({local_test_image_path}) ---")
                result5 = gemini_vision_analyzer_tool._run(
                    image_path_or_url=local_test_image_path,
                    prompt="Describe the main elements and colors in this UI mockup.",
                    max_output_tokens=300
                )
                print(f"Ergebnis 5: {result5}")
            else:
                print(f"\n--- HINWEIS Testfall 5: Lokales Testbild '{local_test_image_path}' nicht gefunden. Bitte für umfassenden Test bereitstellen. ---")

    print("\n--- Lokaler Test für GeminiVisionAnalyzerTool abgeschlossen. ---")
