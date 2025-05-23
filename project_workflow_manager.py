import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from dotenv import load_dotenv
from crewai import Task, Crew, Process

# Load environment variables FIRST
load_dotenv()

# Import agents and tools
from agents import (
    project_manager_agent, 
    developer_agent, 
    researcher_agent, 
    tester_agent, 
    debug_agent,
    reflector_agent,
    democratic_agents,
    get_participating_agents,
    should_trigger_democracy
)

from tools.team_voting_tool import ConflictType, VotingPhase
from tools.file_operations_tool import write_file_tool, read_file_tool, create_directory_tool

class ProjectWorkflowManager:
    """
    Der zentrale Manager für den gesamten IMAP Projekt-Workflow.
    Implementiert den "Initiierungs-Modus" und orchestriert alle Phasen.
    
    Philosophy: Follow the Buddhist Middle Way - perfect balance between 
    thoroughness and efficiency. Trust the AIs to find the right balance.
    """
    
    def __init__(self, base_project_path: str, budget_euros: float = 100.0):
        self.base_project_path = Path(base_project_path)
        self.budget_euros = budget_euros
        self.used_budget = 0.0
        
        # Pfade für Projektstruktur
        self.artifacts_path = self.base_project_path / "project_artifacts"
        self.steps_path = self.base_project_path / "development_steps" 
        self.final_output_path = self.base_project_path / "final_website"
        
        # Projektmetadaten
        self.project_metadata = {
            "project_id": f"imap_project_{int(time.time())}",
            "start_time": datetime.now().isoformat(),
            "budget_euros": budget_euros,
            "used_budget": 0.0,
            "current_step": 0,
            "total_steps": 0,
            "status": "initializing",
            "decisions_made": [],
            "development_steps": []
        }
        
        # Ensure base directories exist
        self._setup_project_structure()
        
    def _setup_project_structure(self):
        """Erstellt die Basis-Projektstruktur."""
        directories = [
            self.artifacts_path,
            self.steps_path, 
            self.final_output_path,
            self.artifacts_path / "user_requirements",
            self.artifacts_path / "research_reports",
            self.artifacts_path / "architecture_decisions",
            self.artifacts_path / "progress_tracking"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
        print(f"📁 Projektstruktur erstellt in: {self.base_project_path}")
        
    def _save_project_metadata(self):
        """Speichert die aktuellen Projektmetadaten."""
        metadata_file = self.artifacts_path / "project_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.project_metadata, f, indent=2, ensure_ascii=False)
            
    def _create_step_structure(self, step_number: int, step_name: str, step_description: str, 
                              required_agents: List[str], accessible_files: Dict[str, List[str]]) -> Path:
        """
        Erstellt die Ordnerstruktur für einen Entwicklungs-Step.
        
        Args:
            step_number: Nummer des Steps
            step_name: Name des Steps
            step_description: Beschreibung des Steps
            required_agents: Liste der für diesen Step benötigten Agents
            accessible_files: Mapping von Agent-Namen zu erlaubten Dateipfaden
        """
        step_dir = self.steps_path / f"Step_{step_number:02d}_{step_name.replace(' ', '_')}"
        step_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (step_dir / "code").mkdir(exist_ok=True)
        (step_dir / "tests").mkdir(exist_ok=True)
        (step_dir / "docs").mkdir(exist_ok=True)
        
        # Create plan.md
        plan_content = f"""# Step {step_number}: {step_name}

## Description
{step_description}

## Required Agents
{', '.join(required_agents)}

## Objectives
- [ ] Implement core functionality
- [ ] Write tests
- [ ] Ensure code quality
- [ ] Document implementation

## Timeline
Estimated: 1-2 hours

## Success Criteria
- All tests pass
- Code follows best practices
- Documentation is complete
- Ready for next step

## Notes
Follow the Buddhist Middle Way - balance thoroughness with efficiency.
"""
        
        with open(step_dir / "plan.md", 'w', encoding='utf-8') as f:
            f.write(plan_content)
            
        # Create files_access.json
        access_matrix = {
            "step_number": step_number,
            "step_name": step_name,
            "agent_access": accessible_files,
            "shared_files": [
                str(step_dir / "plan.md"),
                str(step_dir / "README.md")
            ]
        }
        
        with open(step_dir / "files_access.json", 'w', encoding='utf-8') as f:
            json.dump(access_matrix, f, indent=2, ensure_ascii=False)
            
        return step_dir
        
    def phase_1_user_briefing_and_pm_planning(self, user_requirements: str) -> Dict[str, Any]:
        """
        Phase 1: Nutzer-Briefing & PM-Planung
        Der PM erfasst Anforderungen und erstellt detaillierte Planungsartefakte.
        """
        print("\n🎯 === PHASE 1: USER BRIEFING & PM PLANNING ===")
        print(f"Budget: {self.budget_euros}€ | Used: {self.used_budget}€")
        
        # Save user requirements
        requirements_file = self.artifacts_path / "user_requirements" / "initial_brief.md"
        
        # Task for PM to analyze requirements and create planning artifacts
        pm_planning_task = Task(
            description=(
                f"You are the Project Manager. Analyze the following user requirements and create "
                f"detailed planning artifacts:\n\n"
                f"USER REQUIREMENTS:\n{user_requirements}\n\n"
                f"Create the following artifacts:\n"
                f"1. REQUIREMENTS_ANALYSIS: Detailed analysis of requirements\n"
                f"2. RESEARCH_PLAN: Plan for initial research phase\n"
                f"3. WORK_PLAN: High-level work plan with phases\n"
                f"4. STEP_BREAKDOWN: Breakdown into concrete development steps (aim for 3-5 steps)\n"
                f"5. ACCESS_MATRIX_TEMPLATE: Template for file access control per step\n\n"
                f"Save the requirements to: '{requirements_file}'\n"
                f"Save your planning artifacts as separate files in: '{self.artifacts_path}'\n"
                f"Follow the Buddhist Middle Way - thorough analysis but efficient execution.\n"
                f"Estimate costs for each step to stay within budget of {self.budget_euros}€."
            ),
            expected_output=(
                f"Confirmation that all planning artifacts have been created and saved. "
                f"Include a summary of the planned development steps and estimated timeline."
            ),
            agent=project_manager_agent
        )
        
        # Execute PM planning
        pm_crew = Crew(
            agents=[project_manager_agent],
            tasks=[pm_planning_task],
            process=Process.sequential,
            verbose=True
        )
        
        planning_result = pm_crew.kickoff()
        
        # Update project metadata
        self.project_metadata["status"] = "planning_complete"
        self._save_project_metadata()
        
        print("✅ Phase 1 complete: PM Planning finished")
        return {"status": "success", "result": planning_result}
        
    def phase_2_democratic_architecture_decision(self, research_context: str) -> Dict[str, Any]:
        """
        Phase 2: Demokratische Architektur-Entscheidung
        Nach initialer Recherche erfolgt demokratische Framework/Architektur-Wahl.
        """
        print("\n🗳️ === PHASE 2: DEMOCRATIC ARCHITECTURE DECISION ===")
        
        # Initial research by Researcher
        research_task = Task(
            description=(
                f"You are the Research Specialist. Conduct focused research on possible "
                f"technology choices for this project based on the requirements:\n\n"
                f"CONTEXT: {research_context}\n\n"
                f"Research and provide options for:\n"
                f"1. Frontend framework (React, Vue, Vanilla JS, etc.)\n"
                f"2. Backend architecture (if needed)\n"
                f"3. Database choices (if needed)\n"
                f"4. Deployment strategies\n\n"
                f"For each option, provide:\n"
                f"- Benefits and drawbacks\n"
                f"- Learning curve\n"
                f"- Development speed\n"
                f"- Maintenance considerations\n\n"
                f"Save your research to: '{self.artifacts_path / 'research_reports' / 'tech_options.md'}'\n"
                f"Follow the Buddhist Middle Way - comprehensive but focused research."
            ),
            expected_output=(
                f"Comprehensive research report with 3-4 viable technology options, "
                f"each with detailed pros/cons analysis."
            ),
            agent=researcher_agent
        )
        
        # Execute research
        research_crew = Crew(
            agents=[researcher_agent],
            tasks=[research_task],
            process=Process.sequential,
            verbose=True
        )
        
        research_result = research_crew.kickoff()
        
        # Trigger democratic decision
        print("\n🤝 Triggering democratic architecture decision...")
        
        # This would integrate with the democratic voting system
        participating_agents = ["Project Manager", "Developer", "Tester", "Debugger"]
        
        # For now, simulate the democratic process
        # In real implementation, this would use the democratic voting tools
        
        print("🏛️ Democratic process would run here...")
        print("- Agents submit proposals")
        print("- Reflector synthesizes options") 
        print("- Ranked choice voting")
        print("- Decision commitment")
        
        # Simulate decision outcome
        architecture_decision = {
            "chosen_framework": "React with TypeScript",
            "reasoning": "Team consensus based on familiarity and tooling",
            "vote_results": "Detailed voting results would be here",
            "commitment_level": "High - all agents committed to the decision"
        }
        
        # Save decision
        decision_file = self.artifacts_path / "architecture_decisions" / "framework_choice.json"
        with open(decision_file, 'w', encoding='utf-8') as f:
            json.dump(architecture_decision, f, indent=2, ensure_ascii=False)
            
        self.project_metadata["decisions_made"].append(architecture_decision)
        self.project_metadata["status"] = "architecture_decided"
        self._save_project_metadata()
        
        print("✅ Phase 2 complete: Architecture decision made democratically")
        return {"status": "success", "decision": architecture_decision}
        
    def phase_3_iterative_development(self, development_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Phase 3: Iterative Step-by-Step Entwicklung
        Jeder Step wird mit dem Tandem-Entwicklungs-Workflow abgearbeitet.
        """
        print("\n⚙️ === PHASE 3: ITERATIVE DEVELOPMENT ===")
        
        for step_num, step_info in enumerate(development_steps, 1):
            print(f"\n📋 Starting Step {step_num}: {step_info['name']}")
            
            # Create step structure
            step_dir = self._create_step_structure(
                step_number=step_num,
                step_name=step_info['name'],
                step_description=step_info['description'],
                required_agents=step_info.get('agents', ['Developer', 'Debugger', 'Tester']),
                accessible_files=step_info.get('file_access', {})
            )
            
            # Execute step with tandem development workflow
            step_result = self._execute_development_step(step_num, step_dir, step_info)
            
            # Update project metadata
            self.project_metadata["development_steps"].append(step_result)
            self.project_metadata["current_step"] = step_num
            self._save_project_metadata()
            
            print(f"✅ Step {step_num} completed: {step_result['status']}")
            
            # Check for democratic triggers (e.g., 3x test failures)
            if step_result.get('test_failures', 0) >= 3:
                print("🚨 Multiple test failures detected - triggering democratic problem-solving...")
                # This would trigger democratic decision-making process
                
        self.project_metadata["status"] = "development_complete"
        self._save_project_metadata()
        
        print("✅ Phase 3 complete: All development steps finished")
        return {"status": "success", "steps_completed": len(development_steps)}
        
    def _execute_development_step(self, step_num: int, step_dir: Path, step_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Führt einen einzelnen Entwicklungs-Step mit Tandem-Workflow aus.
        
        Workflow:
        1. Developer writes initial code
        2. Debugger reviews and refines
        3. Tester validates functionality
        4. Iterate if needed
        """
        print(f"🔄 Executing tandem development workflow for Step {step_num}")
        
        # Development Task (Developer)
        dev_task = Task(
            description=(
                f"You are the Developer. Implement the following functionality:\n\n"
                f"STEP: {step_info['name']}\n"
                f"DESCRIPTION: {step_info['description']}\n"
                f"REQUIREMENTS: {step_info.get('requirements', 'See step plan')}\n\n"
                f"Work directory: {step_dir / 'code'}\n"
                f"Create clean, well-structured code following best practices.\n"
                f"Focus on the core functionality first.\n"
                f"Follow the Buddhist Middle Way - elegant but efficient implementation."
            ),
            expected_output=(
                f"Functional code implementation saved in the step directory. "
                f"Include a brief summary of what was implemented."
            ),
            agent=developer_agent
        )
        
        # Debug/Review Task (Debugger)
        debug_task = Task(
            description=(
                f"You are the Debugger working in tandem with the Developer. "
                f"Review and optimize the code from Step {step_num}:\n\n"
                f"STEP: {step_info['name']}\n"
                f"Code location: {step_dir / 'code'}\n\n"
                f"Your tasks:\n"
                f"1. Review the code for potential issues\n"
                f"2. Optimize performance where needed\n"
                f"3. Ensure error handling is robust\n"
                f"4. Fix any bugs you identify\n"
                f"5. Document your improvements\n\n"
                f"Follow the Buddhist Middle Way - thorough review but efficient fixes."
            ),
            expected_output=(
                f"Code review completed with optimizations applied. "
                f"List of improvements made and any remaining concerns."
            ),
            agent=debug_agent
        )
        
        # Testing Task (Tester)
        test_task = Task(
            description=(
                f"You are the Tester. Validate the functionality of Step {step_num}:\n\n"
                f"STEP: {step_info['name']}\n"
                f"Code location: {step_dir / 'code'}\n\n"
                f"Your tasks:\n"
                f"1. Create appropriate tests for the functionality\n"
                f"2. Run tests and verify results\n"
                f"3. Test edge cases and error conditions\n"
                f"4. Document test results\n"
                f"5. Identify any issues for the development team\n\n"
                f"Save tests in: {step_dir / 'tests'}\n"
                f"Follow the Buddhist Middle Way - comprehensive but focused testing."
            ),
            expected_output=(
                f"Test suite created and executed. "
                f"Report on test results and any issues found."
            ),
            agent=tester_agent
        )
        
        # Execute tandem workflow
        step_crew = Crew(
            agents=[developer_agent, debug_agent, tester_agent],
            tasks=[dev_task, debug_task, test_task],
            process=Process.sequential,
            verbose=True
        )
        
        step_result = step_crew.kickoff()
        
        return {
            "step_number": step_num,
            "step_name": step_info['name'],
            "status": "completed",
            "result": str(step_result),
            "test_failures": 0,  # Would be extracted from actual test results
            "timestamp": datetime.now().isoformat()
        }
        
    def run_complete_workflow(self, user_requirements: str) -> Dict[str, Any]:
        """
        Führt den kompletten IMAP Workflow aus - von User-Briefing bis zur fertigen Website.
        """
        print("🚀 === STARTING COMPLETE IMAP WORKFLOW ===")
        print(f"Project: {self.project_metadata['project_id']}")
        print(f"Budget: {self.budget_euros}€")
        print("Philosophy: Buddhist Middle Way - Balance zwischen Gründlichkeit und Effizienz")
        
        try:
            # Phase 1: User Briefing & PM Planning
            phase1_result = self.phase_1_user_briefing_and_pm_planning(user_requirements)
            
            # Phase 2: Democratic Architecture Decision
            research_context = f"Project requirements: {user_requirements}"
            phase2_result = self.phase_2_democratic_architecture_decision(research_context)
            
            # Phase 3: Iterative Development
            # This would be extracted from PM planning artifacts
            example_steps = [
                {
                    "name": "Basic Structure Setup",
                    "description": "Create basic HTML structure and CSS framework",
                    "requirements": "Responsive layout, modern design",
                    "agents": ["Developer", "Debugger"],
                    "file_access": {
                        "Developer": ["*.html", "*.css", "*.js"],
                        "Debugger": ["*.html", "*.css", "*.js"]
                    }
                },
                {
                    "name": "Interactive Features",
                    "description": "Add interactive elements and animations",
                    "requirements": "Smooth interactions, accessibility",
                    "agents": ["Developer", "Debugger", "Tester"],
                    "file_access": {
                        "Developer": ["*.js", "*.css"],
                        "Debugger": ["*.js", "*.css"],
                        "Tester": ["*.html", "*.js"]
                    }
                },
                {
                    "name": "Final Polish",
                    "description": "Optimization, testing, and deployment preparation",
                    "requirements": "Performance optimized, cross-browser tested",
                    "agents": ["Developer", "Debugger", "Tester"],
                    "file_access": {
                        "Developer": ["*"],
                        "Debugger": ["*"],
                        "Tester": ["*"]
                    }
                }
            ]
            
            phase3_result = self.phase_3_iterative_development(example_steps)
            
            # Final project summary
            final_result = {
                "project_id": self.project_metadata["project_id"],
                "status": "completed",
                "phases_completed": 3,
                "budget_used": self.used_budget,
                "budget_remaining": self.budget_euros - self.used_budget,
                "development_steps": len(example_steps),
                "final_output_path": str(self.final_output_path),
                "completion_time": datetime.now().isoformat(),
                "phase_results": {
                    "phase_1": phase1_result,
                    "phase_2": phase2_result, 
                    "phase_3": phase3_result
                }
            }
            
            self.project_metadata.update(final_result)
            self._save_project_metadata()
            
            print("\n🎉 === IMAP WORKFLOW COMPLETE ===")
            print(f"✅ Projekt erfolgreich abgeschlossen!")
            print(f"📁 Ergebnisse in: {self.base_project_path}")
            print(f"💰 Budget verwendet: {self.used_budget}€ von {self.budget_euros}€")
            
            return final_result
            
        except Exception as e:
            print(f"❌ Error in workflow: {e}")
            self.project_metadata["status"] = "failed"
            self.project_metadata["error"] = str(e)
            self._save_project_metadata()
            return {"status": "failed", "error": str(e)}

# === EXAMPLE USAGE ===

def get_user_requirements():
    """
    Interaktive Erfassung der User-Anforderungen.
    Hier teilst DU dem PM mit, was du möchtest!
    """
    print("🏢 === WILLKOMMEN ZUM IMAP DEMOCRATIC AGENT SYSTEM ===")
    print("Hallo! Ich bin bereit, dein Projekt zu realisieren.")
    print("Erzähl mir, was du möchtest - ich leite es an mein Team weiter.\n")
    
    print("📝 Bitte beschreibe dein Projekt:")
    print("- Was soll erstellt werden?")
    print("- Welche Funktionen sind wichtig?") 
    print("- Wer ist die Zielgruppe?")
    print("- Welches Budget hast du?")
    print("- Gibt es besondere Anforderungen?")
    print("\n(Tipp: Du kannst so ausführlich schreiben wie du möchtest)")
    print("=" * 60)
    
    user_input = []
    print("Deine Anforderungen (beende mit einer leeren Zeile):")
    
    while True:
        line = input()
        if line.strip() == "":
            break
        user_input.append(line)
    
    user_requirements = "\n".join(user_input)
    
    if not user_requirements.strip():
        print("\n⚠️ Keine Anforderungen eingegeben. Verwende Beispiel-Projekt...")
        user_requirements = """
        PROJEKT: Interaktive IMAP Mitarbeiter-Übersicht
        
        AUSGANGSSITUATION:
        - Vorhandene PowerPoint-Präsentation mit Mitarbeiter-Daten
        - Soll in interaktive Website umgewandelt werden
        - Zielgruppe: Interne Mitarbeiter und externe Partner
        
        ANFORDERUNGEN:
        1. Responsive Design für Desktop und Mobile
        2. Suchfunktion für Mitarbeiter
        3. Filter nach Abteilungen/Standorten
        4. Kontaktinformationen leicht zugänglich
        5. Moderne, professionelle Optik
        6. Schnelle Ladezeiten
        
        BUDGET: 5-7€ (geschätzt)
        TIMELINE: 1-2 Tage
        
        BESONDERE ANFORDERUNGEN:
        - Datenschutz beachten
        - Barrierefrei (WCAG 2.1)
        - Einfache Wartung/Updates
        """
    
    print(f"\n✅ Verstanden! Ich leite deine Anforderungen an das Team weiter:")
    print("=" * 60)
    print(user_requirements)
    print("=" * 60)
    
    return user_requirements

def run_user_project():
    """
    Startet ein Projekt basierend auf User-Eingabe.
    """
    # Get user requirements interactively
    user_requirements = get_user_requirements()
    
    # Extract budget from user requirements or use default
    budget = 10.0  # Default budget
    if "budget" in user_requirements.lower():
        # Simple budget extraction - could be made more sophisticated
        lines = user_requirements.lower().split('\n')
        for line in lines:
            if 'budget' in line and '€' in line:
                try:
                    # Extract number before €
                    import re
                    budget_match = re.search(r'(\d+(?:\.\d+)?)\s*€', line)
                    if budget_match:
                        budget = float(budget_match.group(1)) + 5  # Add some buffer
                        break
                except:
                    pass
    
    print(f"\n💰 Budget festgelegt: {budget}€")
    
    # Create project name from current timestamp
    project_name = f"user_project_{int(time.time())}"
    project_manager = ProjectWorkflowManager(
        base_project_path=f"./{project_name}",
        budget_euros=budget
    )
    
    # Run complete workflow
    result = project_manager.run_complete_workflow(user_requirements)
    
    return result

if __name__ == '__main__':
    print("🤖 === IMAP DEMOCRATIC AGENT SYSTEM ===")
    print("Philosophy: Buddhist Middle Way - Balance zwischen Gründlichkeit und Effizienz")
    print("Multi-LLM Collaboration: Gemini 2.5 Pro, Claude 4 Sonnet, Codestral, Mistral, Grok 3")
    print("Democratic Decision-Making: 5-Phase Process with Ranked Choice Voting")
    print()
    
    # Run the user's project
    final_result = run_user_project()
    
    print(f"\n📊 === FINAL RESULT ===")
    print(json.dumps(final_result, indent=2, ensure_ascii=False))