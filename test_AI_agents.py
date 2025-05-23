import os
from dotenv import load_dotenv
from crewai import LLM
from pathlib import Path
import time
from datetime import datetime

# Load environment variables
load_dotenv()

# Test message
TEST_MESSAGE = "Hallo, hier ist Rolaf. Welches Modell bist du? Was ist die Definition von Heu? Antworte in einem Satz!"

# Create test directory
test_dir = Path("ai_model_tests")
test_dir.mkdir(exist_ok=True)

print("🧪 === AI MODELS SYSTEMATIC TEST ===")
print(f"Test Message: {TEST_MESSAGE}")
print(f"Results will be saved to: {test_dir}/")
print(f"Timestamp: {datetime.now()}")
print()

# === MODEL DEFINITIONS FROM CURRENT AGENTS.PY ===

models_to_test = [
    {
        "name": "Gemini_2.5_Pro",
        "model": "gemini/gemini-2.5-pro-preview-05-06",  # KORRIGIERT: Mit gemini/ Präfix 
        "api_key_env": "GEMINI_API_KEY",
        "role": "Project Manager"
    },
    {
        "name": "Claude_Sonnet_4", 
        "model": "claude-sonnet-4-20250514",
        "api_key_env": "ANTHROPIC_API_KEY",
        "role": "Developer"
    },
    {
        "name": "Gemini_1.5_Flash",
        "model": "gemini/gemini-1.5-flash", 
        "api_key_env": "GEMINI_API_KEY",
        "role": "Researcher"
    },
    {
        "name": "Mistral_Medium",
        "model": "mistral/mistral-medium-latest",  # KORRIGIERT: Mit mistral/ Präfix
        "api_key_env": "MISTRAL_API_KEY", 
        "role": "Tester"
    },
    {
        "name": "Codestral",
        "model": "mistral/codestral-latest",  # KORRIGIERT: Mit mistral/ Präfix
        "api_key_env": "MISTRAL_API_KEY",
        "role": "Debugger"
    },
    {
        "name": "Grok_3",
        "model": "xai/grok-3-latest",  # KORRIGIERT: Mit xai/ Präfix und -latest
        "api_key_env": "XAI_API_KEY",
        "role": "Reflector"
    }
]

def test_model(model_config):
    """Test a single AI model with cold call."""
    name = model_config["name"]
    model = model_config["model"]
    api_key_env = model_config["api_key_env"]
    role = model_config["role"]
    
    print(f"🤖 Testing {name} ({role})...")
    
    # Check API key
    api_key = os.getenv(api_key_env)
    if not api_key:
        error_msg = f"❌ FAILED: {api_key_env} not found in environment"
        print(f"   {error_msg}")
        
        # Write error to file
        error_file = test_dir / f"{name}_testanswer.md"
        with open(error_file, 'w', encoding='utf-8') as f:
            f.write(f"# {name} Test Result\n\n")
            f.write(f"**Status:** FAILED\n")
            f.write(f"**Error:** {error_msg}\n")
            f.write(f"**Timestamp:** {datetime.now()}\n")
        return False
    
    try:
        # Create LLM instance
        print(f"   Creating LLM with model: {model}")
        llm = LLM(
            model=model,
            api_key=api_key,
            temperature=0.7,
            max_tokens=200
        )
        
        # Test call
        print(f"   Sending test message...")
        start_time = time.time()
        
        # Use LLM call method
        response = llm.call(TEST_MESSAGE)
        
        end_time = time.time()
        response_time = round(end_time - start_time, 2)
        
        print(f"   ✅ SUCCESS: Response received in {response_time}s")
        
        # Write successful response to file
        result_file = test_dir / f"{name}_testanswer.md"
        with open(result_file, 'w', encoding='utf-8') as f:
            f.write(f"# {name} Test Result\n\n")
            f.write(f"**Model:** {model}\n")
            f.write(f"**Role:** {role}\n")
            f.write(f"**Status:** SUCCESS ✅\n")
            f.write(f"**Response Time:** {response_time}s\n")
            f.write(f"**Timestamp:** {datetime.now()}\n\n")
            f.write(f"## Test Question\n")
            f.write(f"{TEST_MESSAGE}\n\n")
            f.write(f"## AI Response\n")
            f.write(f"{response}\n")
        
        return True
        
    except Exception as e:
        error_msg = f"❌ FAILED: {str(e)}"
        print(f"   {error_msg}")
        
        # Write error to file
        error_file = test_dir / f"{name}_testanswer.md"
        with open(error_file, 'w', encoding='utf-8') as f:
            f.write(f"# {name} Test Result\n\n")
            f.write(f"**Model:** {model}\n")
            f.write(f"**Role:** {role}\n")
            f.write(f"**Status:** FAILED ❌\n")
            f.write(f"**Error:** {error_msg}\n")
            f.write(f"**Timestamp:** {datetime.now()}\n")
        
        return False

def main():
    """Run systematic test of all AI models."""
    print("Starting systematic AI model tests...\n")
    
    results = {}
    total_models = len(models_to_test)
    
    for i, model_config in enumerate(models_to_test, 1):
        print(f"[{i}/{total_models}] ", end="")
        success = test_model(model_config)
        results[model_config["name"]] = success
        print()  # Empty line between tests
        
        # Small delay between tests to avoid rate limits
        if i < total_models:
            time.sleep(2)
    
    # Summary
    print("=" * 50)
    print("🏁 TEST SUMMARY")
    print("=" * 50)
    
    successful = sum(results.values())
    failed = total_models - successful
    
    print(f"Total Models Tested: {total_models}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print()
    
    # Detailed results
    for name, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{name:20} {status}")
    
    print()
    print(f"📁 All results saved to: {test_dir}/")
    print("Check individual *_testanswer.md files for detailed responses")
    
    # Summary file
    summary_file = test_dir / "test_summary.md"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("# AI Models Test Summary\n\n")
        f.write(f"**Test Date:** {datetime.now()}\n")
        f.write(f"**Test Message:** {TEST_MESSAGE}\n\n")
        f.write(f"## Results Overview\n")
        f.write(f"- **Total Models:** {total_models}\n")
        f.write(f"- **Successful:** {successful}\n") 
        f.write(f"- **Failed:** {failed}\n\n")
        f.write(f"## Individual Results\n")
        for name, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            f.write(f"- **{name}:** {status}\n")
    
    print(f"📋 Summary saved to: {summary_file}")
    
    if failed > 0:
        print(f"\n⚠️  {failed} model(s) failed. Check error details in individual files.")
        print("This explains why your project_workflow_manager.py might be hanging!")
    else:
        print(f"\n🎉 All models working! Your IMAP system should run smoothly.")

if __name__ == '__main__':
    main()