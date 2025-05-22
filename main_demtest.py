#!/usr/bin/env python3
"""
IMAP Democratic Agent System - Standalone Test
==============================================

Tests the complete democratic decision-making process with a frontend framework selection scenario.
This is a standalone test that doesn't interfere with the existing main.py.

Run with: python main_demtest.py
"""

import os
import json
import time
from dotenv import load_dotenv
from crewai import Task, Crew, Process

# Load environment variables FIRST
load_dotenv()

# Verify required environment variables
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY nicht in .env gefunden! Bitte in der .env Datei eintragen.")

# Set environment variables for consistency
os.environ["GEMINI_API_KEY"] = gemini_api_key
os.environ["GOOGLE_API_KEY"] = gemini_api_key 

lite_llm_model_name = os.getenv("LITELLM_MODEL_NAME", "gemini/gemini-1.5-flash")
os.environ["LITELLM_MODEL_NAME"] = lite_llm_model_name

serper_api_key = os.getenv("SERPER_API_KEY")
if serper_api_key:
    os.environ["SERPER_API_KEY"] = serper_api_key

# Import enhanced agents with democratic capabilities
from agents import (
    project_manager_agent, 
    developer_agent, 
    researcher_agent, 
    tester_agent, 
    debug_agent,
    reflector_agent
)

# Import synthesis tools for reflector
from tools.synthesis_tools import (
    analyze_proposals_tool,
    synthesize_voting_options_tool,
    facilitate_reflection_tool
)

# === PROJECT SETUP ===

script_dir = os.path.dirname(__file__)
democratic_test_path = os.path.join(script_dir, "democratic_test_project")
artifacts_path = os.path.join(democratic_test_path, "agent_artifacts")
application_code_path = os.path.join(democratic_test_path, "application_code")

def setup_test_environment():
    """Erstellt die notwendigen Verzeichnisse für den Test."""
    os.makedirs(artifacts_path, exist_ok=True)
    os.makedirs(application_code_path, exist_ok=True)
    print(f"📁 Test-Verzeichnisse erstellt: {democratic_test_path}")

# === DEMOCRATIC TASKS ===

task_pm_trigger_democracy = Task(
    description=(
        f"You are the Project Manager facilitating a democratic decision. A new web application project needs "
        f"a frontend framework choice - this is a major architectural decision.\n\n"
        f"PROJECT CONTEXT:\n"
        f"- Modern web dashboard for data visualization\n"
        f"- Real-time data updates required\n" 
        f"- Mobile-responsive design\n"
        f"- Team will maintain for 2+ years\n"
        f"- SEO considerations important\n\n"
        f"TASK:\n"
        f"1. Use 'Trigger Democratic Decision Tool' with:\n"
        f"   - conflict_type: 'architecture_decision'\n"
        f"   - trigger_reason: 'Frontend framework selection for data dashboard project'\n"
        f"   - context: 'Need to choose frontend framework considering real-time data, responsive design, maintainability, and SEO'\n"
        f"   - participating_agents: ['Project Manager', 'Developer', 'Researcher', 'Tester']\n\n"
        f"2. Write a project brief to: '{os.path.join(artifacts_path, 'project_context.md')}'\n\n"
        f"Remember: You facilitate, not dictate. Let democracy work!"
    ),
    expected_output=(
        f"Confirmation that democratic decision has been triggered with decision ID. "
        f"Project context saved to file. Ready for team proposal phase."
    ),
    agent=project_manager_agent,
)

task_developer_proposal = Task(
    description=(
        f"You are the Developer contributing to the democratic framework decision.\n\n"
        f"STEPS:\n"
        f"1. Use 'Get Decision Status Tool' to see the current decision details\n"
        f"2. Use 'Submit Proposal Tool' with your technical perspective\n\n"
        f"YOUR DEVELOPER PERSPECTIVE:\n"
        f"- Developer experience and productivity\n"
        f"- Type safety and tooling\n"
        f"- Component reusability\n"
        f"- Build system and development workflow\n"
        f"- Team's existing JavaScript/TypeScript skills\n\n"
        f"Choose ONE specific framework and provide solid technical reasoning. "
        f"Consider: React, Vue.js, Angular, or Svelte."
    ),
    expected_output=(
        f"Your technical proposal submitted to the democratic process with detailed reasoning "
        f"focusing on developer experience and technical implementation."
    ),
    agent=developer_agent,
)

task_researcher_proposal = Task(
    description=(
        f"You are the Researcher providing data-driven input to the framework decision.\n\n"
        f"STEPS:\n"
        f"1. Check decision status with 'Get Decision Status Tool'\n"
        f"2. Submit your research-based proposal with 'Submit Proposal Tool'\n\n"
        f"YOUR RESEARCH PERSPECTIVE:\n"
        f"- Current market adoption and trends (2024/2025)\n"
        f"- Community size and activity\n"
        f"- Documentation quality and learning resources\n"
        f"- Performance benchmarks for data-heavy apps\n"
        f"- Long-term viability and backing\n\n"
        f"Base your recommendation on objective data, not personal preference."
    ),
    expected_output=(
        f"Research-backed proposal submitted with market data and objective analysis "
        f"supporting your framework recommendation."
    ),
    agent=researcher_agent,
)

task_tester_proposal = Task(
    description=(
        f"You are the Tester advocating for quality and user experience in the framework decision.\n\n"
        f"STEPS:\n"
        f"1. Check current decision with 'Get Decision Status Tool'\n"
        f"2. Submit your QA perspective with 'Submit Proposal Tool'\n\n"
        f"YOUR TESTING PERSPECTIVE:\n"
        f"- Testing ecosystem and tools availability\n"
        f"- End-user performance and loading speed\n"
        f"- Accessibility features and support\n"
        f"- Error handling and debugging capabilities\n"
        f"- Real-world usability for data dashboards\n\n"
        f"Think: What framework will deliver the best user experience and be easiest to test?"
    ),
    expected_output=(
        f"User-focused proposal submitted emphasizing testing capabilities, performance, "
        f"and end-user experience considerations."
    ),
    agent=tester_agent,
)

task_reflector_synthesis = Task(
    description=(
        f"You are the Reflector facilitating the synthesis phase of this democratic decision.\n\n"
        f"STEPS:\n"
        f"1. Use 'Get Decision Status Tool' to see all submitted proposals\n"
        f"2. Use 'Analyze Proposals Tool' to understand the different perspectives\n"
        f"3. Use 'Facilitate Reflection Tool' with prompt: 'What are the key trade-offs between different approaches and how might they complement each other?'\n"
        f"4. Use 'Synthesize Voting Options Tool' to create 3-4 clear options\n"
        f"5. Write synthesis summary to: '{os.path.join(artifacts_path, 'synthesis_summary.md')}'\n\n"
        f"FACILITATION PRINCIPLES:\n"
        f"- Stay completely neutral\n"
        f"- Preserve the essence of each perspective\n"
        f"- Look for ways different views can strengthen the final decision\n"
        f"- Ask meta-questions that help the team think deeper\n\n"
        f"Your role: Mirror the collective intelligence, don't add your own technical opinions."
    ),
    expected_output=(
        f"Complete synthesis with clear voting options created. Decision advanced to voting phase. "
        f"Synthesis summary saved showing how different perspectives were integrated."
    ),
    agent=reflector_agent,
)

task_pm_finalize = Task(
    description=(
        f"You are the Project Manager concluding the democratic decision process.\n\n"
        f"STEPS:\n"
        f"1. Use 'Get Decision Status Tool' to see synthesized voting options\n"
        f"2. Select the option that best integrates all team perspectives\n"
        f"3. Write final decision to: '{os.path.join(artifacts_path, 'final_decision.md')}'\n\n"
        f"FINAL DECISION SHOULD INCLUDE:\n"
        f"- The chosen framework and implementation approach\n"
        f"- How each team member's input influenced the decision\n"
        f"- Why this collective choice is better than any individual preference\n"
        f"- Next steps for implementation\n"
        f"- Team commitment statement\n\n"
        f"This represents the COMMITMENT phase where everyone supports the collective decision."
    ),
    expected_output=(
        f"Final democratic decision documented showing how collective intelligence led to a better "
        f"choice than individual decision-making. All team perspectives integrated."
    ),
    agent=project_manager_agent,
)

# === DEMOCRATIC CREW ===

democratic_crew = Crew(
    agents=[
        project_manager_agent,
        developer_agent, 
        researcher_agent,
        tester_agent,
        reflector_agent
    ],
    tasks=[
        task_pm_trigger_democracy,
        task_developer_proposal,
        task_researcher_proposal, 
        task_tester_proposal,
        task_reflector_synthesis,
        task_pm_finalize
    ],
    process=Process.sequential,
    verbose=True
)

def run_democratic_test():
    """Führt den vollständigen demokratischen Entscheidungstest durch."""
    print("🗳️" + "="*70)
    print("🗳️  IMAP DEMOCRATIC AGENT SYSTEM - LIVE TEST")
    print("🗳️" + "="*70)
    print("🗳️  Testing: Collective Intelligence vs Individual Decision-Making")
    print("🗳️  Scenario: Frontend Framework Selection Conflict")
    print("🗳️  Participants: PM, Developer, Researcher, Tester + Reflector")
    print("🗳️" + "="*70)
    
    setup_test_environment()
    
    try:
        start_time = time.time()
        
        print(f"\n🚀 Launching democratic decision-making process...")
        print(f"📁 Artifacts will be saved to: {artifacts_path}")
        
        # Run the democratic crew
        result = democratic_crew.kickoff()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "🎉"*70)
        print("🎉 DEMOCRATIC DECISION-MAKING COMPLETE!")
        print(f"🎉 Total Duration: {duration:.1f} seconds")
        print("🎉" + "="*68)
        
        print(f"\n📋 FINAL CREW RESULT:")
        print("-" * 50)
        print(result)
        
        # Display generated artifacts
        print(f"\n📁 GENERATED ARTIFACTS:")
        print("-" * 30)
        
        artifact_files = [
            ("project_context.md", "Project Context (PM)"),
            ("synthesis_summary.md", "Synthesis Summary (Reflector)"), 
            ("final_decision.md", "Final Decision (Collective)")
        ]
        
        for filename, description in artifact_files:
            filepath = os.path.join(artifacts_path, filename)
            if os.path.exists(filepath):
                print(f"✅ {description}")
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    preview = content[:150].replace('\n', ' ')
                    print(f"   📄 {preview}...")
                    print(f"   📂 Full file: {filepath}")
            else:
                print(f"❌ {description} (not created)")
            print()
        
        print("🔍 ANALYSIS COMPLETE!")
        print("💡 Check the artifacts to see how collective intelligence works!")
        
        return result
        
    except Exception as e:
        print(f"\n❌ ERROR during democratic test: {e}")
        import traceback
        traceback.print_exc()
        return None

def run_quick_tools_test():
    """Schneller Test nur der demokratischen Tools."""
    print("🛠️ QUICK DEMOCRACY TOOLS TEST")
    print("-" * 40)
    
    from tools.team_voting_tool import (
        trigger_democratic_decision_tool,
        submit_proposal_tool,
        get_decision_status_tool
    )
    
    try:
        # 1. Trigger
        print("1️⃣ Triggering decision...")
        result1 = trigger_democratic_decision_tool._run(
            conflict_type="architecture_decision",
            trigger_reason="Quick test framework choice",
            context="Testing democratic tools with React vs Vue choice",
            participating_agents=["Developer", "Tester"]
        )
        print(f"✅ {result1}")
        
        # Extract decision ID
        if "ID: " in result1:
            decision_id = result1.split("ID: ")[1].split(".")[0]
            
            # 2. Proposals
            print(f"\n2️⃣ Submitting proposals...")
            prop1 = submit_proposal_tool._run(
                decision_id=decision_id,
                agent_name="Developer", 
                proposal="React with TypeScript",
                reasoning="Strong typing and excellent tooling"
            )
            prop2 = submit_proposal_tool._run(
                decision_id=decision_id,
                agent_name="Tester",
                proposal="Vue.js 3 with Composition API",
                reasoning="Better testing experience and simpler debugging"
            )
            print(f"✅ Developer: {prop1}")
            print(f"✅ Tester: {prop2}")
            
            # 3. Status
            print(f"\n3️⃣ Final status...")
            status = get_decision_status_tool._run(decision_id=decision_id)
            status_data = json.loads(status)
            print(f"✅ Decision {decision_id} in phase: {status_data.get('current_phase')}")
            print(f"✅ Proposals: {len(status_data.get('proposals', []))}")
            
            print(f"\n🎯 Democracy tools working correctly!")
        else:
            print(f"❌ Could not extract decision ID from: {result1}")
        
    except Exception as e:
        print(f"❌ Tools test error: {e}")

if __name__ == '__main__':
    print("🌟 IMAP Democratic Agent System")
    print("Choose test mode:")
    print("1. Full Democratic Test (complete 5-phase process)")
    print("2. Quick Tools Test (just verify tools work)")
    
    choice = input("\nEnter choice (1 or 2, default=1): ").strip()
    
    if choice == "2":
        print("\n" + "="*50)
        run_quick_tools_test()
    else:
        print("\n" + "="*50)
        run_democratic_test()
    
    print("\n🎉 Test complete! Check the artifacts to see collective intelligence in action!")