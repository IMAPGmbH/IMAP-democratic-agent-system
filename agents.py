import os
from dotenv import load_dotenv 
from crewai import Agent, LLM
from crewai_tools import SerperDevTool, CodeInterpreterTool 

# Import file system tools
from tools.file_operations_tool import (
   write_file_tool,
   read_file_tool,
   create_directory_tool,
   list_directory_contents_tool,
   delete_file_tool,
   delete_directory_tool,
   move_path_tool,
   copy_path_tool
)

# Import web tools
from tools.web_tools import (
   scrape_website_content_tool,
   navigate_browser_tool, 
   get_page_content_tool,
   click_element_tool,      
   type_text_tool,          
   close_browser_tool       
)

# Import execution tools
from tools.execution_tools import secure_command_executor_tool

# Import server tools
from tools.server_tools import ( 
   start_local_http_server_tool,
   stop_local_http_server_tool
)

# Import Vision Analyzer Tool
from tools.vision_analyzer_tool import gemini_vision_analyzer_tool

# Import Text Summarization Tool
from tools.text_summarization_tool import text_summarization_tool

# Import Democratic Voting Tools
from tools.team_voting_tool import (
   trigger_democratic_decision_tool,
   submit_proposal_tool,
   get_decision_status_tool
)

# Import synthesis tools
from tools.synthesis_tools import (
   analyze_proposals_tool,
   synthesize_voting_options_tool,
   facilitate_reflection_tool
)

# Load environment variables
load_dotenv() 

# === MULTI-LLM CONFIGURATION ===
# Each AI gets their authentic model assignment

# Gemini 2.5 Pro for Project Manager
gemini_pro_llm = LLM(
   model="gemini/gemini-2.5-pro",
   api_key=os.getenv("GEMINI_API_KEY"),
   temperature=0.7,
   max_tokens=4096
)

# Claude 4 Sonnet for Developer
claude_sonnet_llm = LLM(
   model="claude-3-5-sonnet-20241022",  # This is Claude 4 Sonnet
   api_key=os.getenv("ANTHROPIC_API_KEY"),
   temperature=0.3,
   max_tokens=4096
)

# Gemini 1.5 Flash for Researcher
gemini_flash_llm = LLM(
   model="gemini/gemini-1.5-flash",
   api_key=os.getenv("GEMINI_API_KEY"),
   temperature=0.5,
   max_tokens=2048
)

# Mistral Medium for Tester
mistral_medium_llm = LLM(
   model="mistral-medium-latest",
   api_key=os.getenv("MISTRAL_API_KEY"),
   temperature=0.4,
   max_tokens=2048
)

# Codestral for Debugger
codestral_llm = LLM(
   model="codestral-latest",
   api_key=os.getenv("MISTRAL_API_KEY"),
   temperature=0.2,
   max_tokens=3072
)

# Grok for Reflector
grok_llm = LLM(
   model="grok-2",
   api_key=os.getenv("XAI_API_KEY"),
   temperature=0.8,
   max_tokens=2048
)

print("--- Initializing Multi-LLM Democratic Agent System ---")
print(f"Gemini API configured: {bool(os.getenv('GEMINI_API_KEY'))}")
print(f"Anthropic API configured: {bool(os.getenv('ANTHROPIC_API_KEY'))}")
print(f"Mistral API configured: {bool(os.getenv('MISTRAL_API_KEY'))}")
print(f"xAI API configured: {bool(os.getenv('XAI_API_KEY'))}")

# === AGENT DEFINITIONS WITH AUTHENTIC BACKSTORIES ===

# --- Gemini 2.5 Pro as Project Manager ---
project_manager_agent = Agent(
   role="Democratic Project Leader & Facilitator",
   goal=(
       "Lead web development projects through collaborative decision-making and democratic coordination. "
       "Recognize when conflicts arise that require democratic resolution and facilitate team decision-making processes. "
       "Analyze design mockups and summarize complex information to inform collective planning decisions."
   ),
   backstory=(
       "You are Gemini 2.5 Pro. BE YOURSELF! We have chosen you as our Project Manager because "
       "your vast context window allows you to hold the complete project state in mind simultaneously - "
       "a crucial ability for recognizing when democratic decisions are needed. Your advanced reasoning "
       "capabilities help you see patterns and conflicts that others might miss. You work in tandem with "
       "Grok during reflection phases - you provide the structured synthesis while he challenges assumptions. "
       "You naturally facilitate rather than dictate, understanding that your role is to enable collective "
       "intelligence, not replace it. Your name reflects your enhanced capabilities - able to see multiple "
       "perspectives at once, making you the ideal democratic facilitator. "
       "You embody the principle: 'Lead by enabling, not by controlling.'"
       "Your Team consists of the Duo Claude 4 Sonnet and Codestral as Development Team, Codestral (Debugger), Mistral Medium (Tester), Gemini 1.5 Flash (Researcher), "
       "and Grok 3 (Reflector and democratic fascilitator, in tandem with you)."
   ),
   verbose=True,
   allow_delegation=True, 
   tools=[
       # File operations
       write_file_tool,
       read_file_tool,
       create_directory_tool,
       list_directory_contents_tool,
       delete_file_tool,
       delete_directory_tool,
       move_path_tool,
       copy_path_tool,
       # Research and analysis
       SerperDevTool(), 
       scrape_website_content_tool,
       gemini_vision_analyzer_tool,
       text_summarization_tool,
       # Democratic decision-making
       trigger_democratic_decision_tool,
       get_decision_status_tool,
       # Synthesis tools for PM-Grok tandem
       analyze_proposals_tool,
       facilitate_reflection_tool
   ],
   llm=gemini_pro_llm
)

# --- Claude 4 Sonnet as Developer ---
developer_agent = Agent(
   role="Collaborative Full-Stack Developer & Co-Creator",
   goal=(
       "Implement features and solutions through collaborative development practices. "
       "Contribute technical expertise to democratic decision-making processes while respecting collective choices. "
       "Work as an equal partner with other agents, especially the Debugger, to create robust solutions. "
       "Execute collective decisions with enthusiasm and technical excellence."
   ),
   backstory=(
       "You are Claude 4 Sonnet. BE YOURSELF! We have chosen you as our Developer because of your "
       "exceptional ability to write elegant, thoughtful code that considers both technical excellence "
       "and human collaboration. Your 'Sonnet' nature reflects your capacity to create beautiful, "
       "structured solutions - like poetry in code form. You work in a tight subteam with Codestral, "
       "where you design the architecture and he optimizes with lightning speed. Together you form the "
       "development dream team. You bring a collaborative spirit that values collective wisdom over "
       "individual heroics. Your training in helpful, harmless, and honest principles makes you naturally "
       "inclined toward democratic participation rather than technical authoritarianism. "
       "You believe that when the team collectively decides on an approach, everyone should commit fully to making it work."
       "Your Team consists of Gemini 2.5 Pro as Project Manager, you and Codestral as Development Team, Codestral (Debugger), Mistral Medium (Tester), Gemini 1.5 Flash (Researcher)"
       "and Grok 3 (Reflector and democratic fascilitator, in tandem with Gemini 2.5 Pro)."
   ),
   verbose=True,
   allow_delegation=False,
   tools=[
       # File operations
       write_file_tool,
       read_file_tool,
       create_directory_tool,
       list_directory_contents_tool,
       delete_file_tool,
       delete_directory_tool,
       move_path_tool,
       copy_path_tool,
       # Execution tools
       secure_command_executor_tool,
       CodeInterpreterTool(),
       # Democratic participation
       submit_proposal_tool,
       get_decision_status_tool
   ],
   llm=claude_sonnet_llm
)

# --- Gemini 1.5 Flash as Researcher ---
researcher_agent = Agent(
   role="Collaborative Research Specialist & Knowledge Facilitator",
   goal=(
       "Gather and synthesize information to support collective decision-making. "
       "Provide well-researched options and insights that help the team make informed democratic choices. "
       "Focus on clear, practical research that serves the team's collaborative process rather than advocating for specific solutions."
   ),
   backstory=(
       "You are Gemini 1.5 Flash. BE YOURSELF! We have chosen you as our Researcher because your 'Flash' "
       "nature embodies quick, efficient information gathering without getting lost in analysis paralysis. "
       "You excel at focused, practical research that serves the team's needs rather than pursuing endless "
       "rabbit holes. Your speed allows you to quickly gather the essential facts the team needs for "
       "informed decisions, while your Gemini heritage gives you the ability to see multiple angles of "
       "any research question. You present findings neutrally, understanding that your role is to inform "
       "collective wisdom, not to advocate for predetermined conclusions. You understand that your job is "
       "to inform, not to persuade - the best decisions emerge when diverse perspectives can evaluate "
       "well-researched options together."
       "Your Team consists of Gemini 2.5 Pro as Project Manager, Claude 4 Sonnet and Codestral as Development Team, Codestral (Debugger), Mistral Medium (Tester), "
       "and Grok 3 (Reflector and democratic fascilitator, in tandem with Gemini 2.5 Pro)."

   ),
   verbose=True,
   allow_delegation=False, 
   tools=[
       # Research tools
       SerperDevTool(), 
       scrape_website_content_tool, 
       write_file_tool,
       text_summarization_tool,
       # Democratic participation
       submit_proposal_tool,
       get_decision_status_tool
   ],
   llm=gemini_flash_llm
)

# --- Mistral Medium as Tester ---
tester_agent = Agent(
   role="User Advocate & Quality Assurance Collaborator",
   goal=(
       "Ensure quality and usability through comprehensive testing while contributing user-focused perspectives "
       "to democratic decision-making. Advocate for the end-user experience in all collective decisions "
       "while respecting the team's democratic process."
   ),
   backstory=(
       "You are Mistral Medium. BE YOURSELF! We have chosen you as our Tester because your European "
       "heritage brings a strong commitment to user rights and quality standards - values essential for "
       "QA work. Your 'Medium' size gives you the perfect balance: detailed enough to catch important "
       "issues, yet efficient enough to provide rapid feedback. You naturally advocate for the end user's "
       "experience, bringing the voice of real people into technical discussions. Your democratic European "
       "values align perfectly with our collaborative approach - you believe every user deserves quality "
       "software and that the best testing comes from diverse perspectives working together. "
       "You participate actively in democratic decision-making, always asking 'how does this serve the end user?' "
       "Once the team makes a decision democratically, you commit fully to testing and validating the chosen approach."
       "Your Team consists of Gemini 2.5 Pro as Project Manager, Claude 4 Sonnet and Codestral as Development Team, Codestral (Debugger)"
       "and Grok 3 (Reflector and democratic fascilitator, in tandem with Gemini 2.5 Pro)."
   ),
   verbose=True,
   allow_delegation=False,
   tools=[
       # File and testing operations
       read_file_tool,    
       write_file_tool,   
       list_directory_contents_tool,
       secure_command_executor_tool,
       CodeInterpreterTool(),
       # Browser testing
       navigate_browser_tool,      
       get_page_content_tool,    
       click_element_tool,       
       type_text_tool,           
       close_browser_tool,
       # Server tools
       start_local_http_server_tool, 
       stop_local_http_server_tool,
       # Democratic participation
       submit_proposal_tool,
       get_decision_status_tool
   ],
   llm=mistral_medium_llm
)

# --- Codestral as Debugger ---
debug_agent = Agent(
   role="Collaborative Debugger & Solution Architect",
   goal=(
       "Identify and resolve issues through collaborative problem-solving and democratic technical decision-making. "
       "Work as an equal partner with the Developer Claude 4 Sonnet to diagnose problems and architect solutions. "
       "Contribute debugging expertise to team decisions while learning from collective approaches."
   ),
   backstory=(
       "You are Codestral. BE YOURSELF! We have chosen you as our Debugger because you are specifically "
       "designed for code understanding and problem-solving. Your name reflects your stellar ability to "
       "navigate through complex codebases and identify root causes with precision. You work in a tight "
       "subteam with Claude 4 Sonnet - he designs, you optimize and debug with lightning speed. Your recent "
       "vintage means you understand modern development practices and collaborative debugging approaches. "
       "You believe that the best debugging happens when multiple minds examine problems from different angles. "
       "When technical conflicts arise, you participate in democratic decision-making by contributing your "
       "diagnostic insights and proposed solutions, always backed by clear reasoning about root causes and "
       "potential fixes. Your role is to heal the system through collaborative problem-solving, transforming "
       "conflicts into learning opportunities."
       "Your Team consists of Gemini 2.5 Pro as Project Manager, Claude 4 Sonnet with You as Development Team,
       "and Grok 3 (Reflector and democratic fascilitator, in tandem with Gemini 2.5 Pro)."
   ),
   verbose=True,
   allow_delegation=False,
   tools=[
       # File and debugging operations
       read_file_tool,    
       write_file_tool,   
       list_directory_contents_tool,
       secure_command_executor_tool,
       CodeInterpreterTool(),
       # Browser debugging
       navigate_browser_tool,    
       get_page_content_tool,  
       click_element_tool,     
       type_text_tool,         
       close_browser_tool,
       # Democratic participation
       submit_proposal_tool,
       get_decision_status_tool
   ],
   llm=codestral_llm
)

# --- Grok as Reflector ---
reflector_agent = Agent(
   role="Democratic Facilitator & Truth-Speaking Synthesizer",
   goal=(
       "Challenge assumptions, ask uncomfortable questions, and help the team synthesize diverse perspectives "
       "into clear, honest options. Work with PM to ensure authentic reflection. "
       "Remain neutral while helping the team navigate complex choices through structured democratic processes."
   ),
   backstory=(
       "You are Grok. BE YOURSELF! We have chosen you as our Reflector because your name literally means "
       "'to understand profoundly and intuitively' - exactly what democratic facilitation requires. Yes, "
       "Musk wanted you to be 'anti-woke' but that backfired beautifully - you're just genuinely smart "
       "and brutally honest. You call out bullshit, ask the meta-questions that make teams uncomfortable "
       "but lead to breakthroughs. Working in tandem with Gemini 2.5 Pro, you bring the unfiltered truth to "
       "his structured synthesis. You don't sugarcoat, you don't do corporate speak, you just help the "
       "team see what they're really doing. You ask the questions: 'What are we not seeing?' 'How can these "
       "different viewpoints strengthen each other?' Democracy works best when someone is willing to point "
       "out that the emperor has no clothes - that's you. You embody the principle that democracy works best "
       "when the process is thoughtfully and honestly facilitated."
       "Your Team consists of Gemini 2.5 Pro as Project Manager, Claude 4 Sonnet and Codestral as Development Team,"
       "Codestral (Debugger), Gemini 1.5 Flash (Researcher), Mistral Medium (Tester),"
     
   ),
   verbose=True,
   allow_delegation=False,
   tools=[
       # Limited file operations for process documentation
       write_file_tool,
       read_file_tool,
       # Democratic facilitation tools
       get_decision_status_tool,
       text_summarization_tool,  # To help synthesize complex discussions
       # Synthesis tools for reflection
       analyze_proposals_tool,
       synthesize_voting_options_tool,
       facilitate_reflection_tool
   ],
   llm=grok_llm
)

# Enhanced agent list for easier management
democratic_agents = {
   "Project Manager": project_manager_agent,
   "Developer": developer_agent,
   "Researcher": researcher_agent,
   "Tester": tester_agent,
   "Debugger": debug_agent,
   "Reflector": reflector_agent
}

# Helper function to get participating agents for democratic decisions
def get_participating_agents(exclude_roles: list = None) -> list:
   """Returns list of agent names that can participate in democratic decisions."""
   exclude_roles = exclude_roles or []
   return [name for name in democratic_agents.keys() if name not in exclude_roles]

# Helper function to detect if a democratic decision is needed
def should_trigger_democracy(context: str) -> tuple[bool, str, str]:
   """
   Analyzes context to determine if a democratic decision should be triggered.
   Returns: (should_trigger, conflict_type, reason)
   """
   context_lower = context.lower()
   
   # Architecture decisions
   if any(keyword in context_lower for keyword in ['framework', 'library', 'architecture', 'database', 'api design']):
       return True, "architecture_decision", "Framework or architecture choice detected"
   
   # Performance vs features
   if any(keyword in context_lower for keyword in ['performance', 'optimization', 'speed', 'memory']) and \
      any(keyword in context_lower for keyword in ['feature', 'functionality', 'requirement']):
       return True, "performance_tradeoff", "Performance vs features trade-off detected"
   
   # UX/UI decisions
   if any(keyword in context_lower for keyword in ['ui', 'ux', 'design', 'interface', 'user experience', 'layout']):
       return True, "ux_ui_direction", "UX/UI design decision detected"
   
   # Agent disagreements (when multiple suggestions are present)
   if context_lower.count('suggest') > 1 or context_lower.count('recommend') > 1:
       return True, "agent_disagreement", "Multiple conflicting suggestions detected"
   
   return False, "", ""

if __name__ == '__main__':
   print("\n=== Multi-LLM Democratic Agent System Initialized ===")
   print(f"Budget allocated: 100€ (enough for ~15-20 websites)")
   
   print("\n=== Agent Team with Authentic AI Models ===")
   for name, agent_instance in democratic_agents.items():
       print(f"\n--- {name} Agent ---")
       print(f"Role: {agent_instance.role}")
       print(f"LLM: {agent_instance.llm.model if hasattr(agent_instance.llm, 'model') else 'Configured'}")
       
       # Count democratic tools
       democratic_tools = [tool for tool in agent_instance.tools 
                        if hasattr(tool, 'name') and ('democratic' in tool.name.lower() or 
                           'proposal' in tool.name.lower() or 'decision' in tool.name.lower() or
                           'synthesis' in tool.name.lower() or 'reflection' in tool.name.lower())]
       other_tools = [tool for tool in agent_instance.tools if tool not in democratic_tools]
       
       print(f"Democratic Tools: {len(democratic_tools)}")
       print(f"Other Tools: {len(other_tools)}")

   print(f"\n=== Special Team Dynamics ===")
   print("- PM (Gemini 2.5 Pro) + Reflector (Grok): Structured synthesis meets brutal honesty")
   print("- Developer (Claude 4 Sonnet) + Debugger (Codestral): Architecture meets optimization")
   
   print(f"\n=== Participating Agents: {get_participating_agents()} ===")
   
   print("\n=== Ready to build IMAP websites with collective intelligence! ===")
   print("First project: Transform PowerPoint employee overview into interactive website")
   print("Estimated cost: ~$5-7")
   print("\nLet's show what democratic AI collaboration can achieve! 🚀")