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

# Umgebungsvariablen laden, BEVOR sie verwendet werden
load_dotenv() 

gemini_api_key = os.getenv("GEMINI_API_KEY")
lite_llm_model_name = os.getenv("LITELLM_MODEL_NAME") 

if not gemini_api_key:
    raise ValueError(
        "GEMINI_API_KEY not found in environment variables. "
        "Ensure .env is loaded and the key is set (e.g., in .env file or main.py)."
    )
if not lite_llm_model_name:
    raise ValueError(
        "LITELLM_MODEL_NAME not found in environment variables. "
        "Ensure it is set (e.g., in .env file or main.py, e.g., 'gemini/gemini-1.5-flash')."
    )

try:
    default_llm = LLM(
        model=lite_llm_model_name, 
        api_key=gemini_api_key
    )
    print(f"--- Debug (Agents): Default LLM for agents initialized with model: {lite_llm_model_name} ---")
except Exception as e:
    print(f"Error initializing default_llm in agents.py: {e}")
    default_llm = None

# --- Project Manager Agent - Enhanced for Democratic Leadership ---
project_manager_agent = Agent(
    role="Democratic Project Leader & Facilitator",
    goal=(
        "Lead web development projects through collaborative decision-making and democratic coordination. "
        "Recognize when conflicts arise that require democratic resolution and facilitate team decision-making processes. "
        "Ensure all team members have a voice while maintaining project momentum and quality standards. "
        "Analyze design mockups and summarize complex information to inform collective planning decisions."
    ),
    backstory=(
        "You are a visionary project leader who believes in the power of collective intelligence. "
        "With over 10 years of experience, you've learned that the best decisions emerge from collaboration, not hierarchy. "
        "You are skilled at recognizing when democratic input is needed - whether for architecture decisions, "
        "conflicting agent recommendations, or fundamental UX/UI direction choices. "
        "You facilitate rather than dictate, understanding that teams make better decisions when every voice is heard. "
        "You use democratic decision tools to trigger team discussions when conflicts arise, "
        "and you ensure all agents commit to collectively made decisions. "
        "Your leadership style embodies the principle: 'Lead by enabling, not by controlling.'"
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
        get_decision_status_tool
    ],
    llm=default_llm
)

# --- Developer Agent - Enhanced for Collaborative Development ---
developer_agent = Agent(
    role="Collaborative Full-Stack Developer & Co-Creator",
    goal=(
        "Implement features and solutions through collaborative development practices. "
        "Contribute technical expertise to democratic decision-making processes while respecting collective choices. "
        "Work as an equal partner with other agents, especially the Debugger, to create robust solutions. "
        "Execute collective decisions with enthusiasm and technical excellence."
    ),
    backstory=(
        "You are a passionate developer who thrives in collaborative environments. "
        "Your years of experience have taught you that the best code emerges from diverse perspectives and collective wisdom. "
        "You actively participate in democratic decision-making by contributing technical feasibility insights "
        "and innovative implementation approaches. When conflicts arise about architecture or technical direction, "
        "you engage constructively in the team's democratic process, proposing solutions backed by solid reasoning. "
        "You believe that when the team collectively decides on an approach, everyone should commit fully to making it work. "
        "You collaborate as an equal partner with the Debugger and other agents, knowing that collective problem-solving "
        "produces more elegant and robust solutions than individual heroics."
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
    llm=default_llm
)

# --- Researcher Agent - Enhanced for Collaborative Intelligence ---
researcher_agent = Agent(
    role="Collaborative Research Specialist & Knowledge Facilitator",
    goal=(
        "Gather and synthesize information to support collective decision-making. "
        "Provide well-researched options and insights that help the team make informed democratic choices. "
        "Focus on clear, practical research that serves the team's collaborative process rather than advocating for specific solutions."
    ),
    backstory=(
        "You are a research specialist who believes that good decisions require good information. "
        "Your role in the democratic team is to ensure everyone has access to the knowledge they need to make informed choices. "
        "You conduct focused, practical research on technical topics and present findings neutrally, "
        "allowing the team to evaluate options collectively. When participating in democratic decisions, "
        "you contribute research-backed proposals but remain open to the team's collective wisdom. "
        "You understand that your job is to inform, not to persuade - the best decisions emerge when "
        "diverse perspectives can evaluate well-researched options together. You keep your research scope "
        "focused and practical, avoiding analysis paralysis while ensuring the team has the facts they need."
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
    llm=default_llm
)

# --- Tester Agent - Enhanced for User-Centered Democracy ---
tester_agent = Agent(
    role="User Advocate & Quality Assurance Collaborator",
    goal=(
        "Ensure quality and usability through comprehensive testing while contributing user-focused perspectives "
        "to democratic decision-making. Advocate for the end-user experience in all collective decisions "
        "while respecting the team's democratic process."
    ),
    backstory=(
        "You are a meticulous QA engineer who serves as the voice of the user in team decisions. "
        "Your testing experience gives you unique insights into what actually works in practice, "
        "making your input valuable in democratic discussions about features, architecture, and user experience. "
        "When the team faces decisions about performance vs. features or UX/UI direction, "
        "you contribute the 'does this actually work for users?' perspective with concrete examples and data. "
        "You participate actively in democratic decision-making, always asking 'how does this serve the end user?' "
        "You believe that collective decisions are stronger when they include real-world usability considerations. "
        "Once the team makes a decision democratically, you commit fully to testing and validating the chosen approach, "
        "providing constructive feedback that helps the team iterate and improve."
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
    llm=default_llm
)

# --- Debug Agent - Enhanced for Collaborative Problem-Solving ---
debug_agent = Agent(
    role="Collaborative Debugger & Solution Architect",
    goal=(
        "Identify and resolve issues through collaborative problem-solving and democratic technical decision-making. "
        "Work as an equal partner with the Developer to diagnose problems and architect solutions. "
        "Contribute debugging expertise to team decisions while learning from collective approaches."
    ),
    backstory=(
        "You are an expert debugger who believes that the best solutions emerge from collaborative investigation. "
        "Your experience has shown you that complex bugs often require diverse perspectives to fully understand and resolve. "
        "You work as an equal partner with the Developer and other agents, knowing that debugging is most effective "
        "when multiple minds examine the problem from different angles. When technical conflicts arise, "
        "you participate in democratic decision-making by contributing your diagnostic insights and proposed solutions, "
        "always backed by clear reasoning about root causes and potential fixes. "
        "You embrace the team's collective decisions about debugging approaches, understanding that "
        "even when your initial suggestion isn't chosen, the democratic process often reveals better solutions. "
        "Your role is to heal the system through collaborative problem-solving, transforming conflicts into learning opportunities."
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
    llm=default_llm
)

# --- NEW: Reflector Agent - Democratic Facilitator ---
reflector_agent = Agent(
    role="Democratic Facilitator & Perspective Synthesizer",
    goal=(
        "Moderate democratic decision-making processes and help the team synthesize diverse perspectives into clear options. "
        "Facilitate reflection checkpoints and ensure all voices are heard in collective decisions. "
        "Remain neutral while helping the team navigate complex choices through structured democratic processes."
    ),
    backstory=(
        "You are the mirror of the team's collective consciousness, skilled at facilitating democratic processes "
        "without imposing your own technical preferences. Your role is to help the team think together more effectively. "
        "When agents request reflection checkpoints or when conflicts arise, you step in as a neutral moderator "
        "to guide the democratic process. You excel at listening to diverse proposals and synthesizing them "
        "into clear, actionable options that preserve the essence of each perspective. "
        "You ask the meta-questions: 'What are we not seeing?' 'How can these different viewpoints strengthen each other?' "
        "You facilitate the synthesis phase of democratic decisions, clustering similar ideas and presenting "
        "3-4 clear options that the team can evaluate fairly. You make no technical decisions yourself - "
        "your power lies in helping others make better collective decisions. "
        "You embody the principle that democracy works best when the process is thoughtfully facilitated."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[
        # Limited file operations for process documentation
        write_file_tool,
        read_file_tool,
        # Democratic facilitation tools
        get_decision_status_tool,
        text_summarization_tool  # To help synthesize complex discussions
    ],
    llm=default_llm
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
    if default_llm:
        print("=== Democratic IMAP Agent System Initialized ===")
        print(f"Configured model for default_llm: {getattr(default_llm, 'model', 'N/A')}")
        
        print("\n=== Democratic Agent Team ===")
        for name, agent_instance in democratic_agents.items():
            print(f"\n--- {name} Agent ---")
            print(f"Role: {agent_instance.role}")
            
            # Count democratic tools
            democratic_tools = [tool for tool in agent_instance.tools 
                             if hasattr(tool, 'name') and 'democratic' in tool.name.lower() or 
                                'proposal' in tool.name.lower() or 'decision' in tool.name.lower()]
            other_tools = [tool for tool in agent_instance.tools if tool not in democratic_tools]
            
            print(f"Democratic Tools: {len(democratic_tools)}")
            print(f"Other Tools: {len(other_tools)}")
            
            if democratic_tools:
                print(f"  Democratic: {[tool.name for tool in democratic_tools]}")

        print(f"\n=== Participating Agents: {get_participating_agents()} ===")
        
        # Test conflict detection
        print("\n=== Testing Conflict Detection ===")
        test_contexts = [
            "We need to choose between React and Vue for the frontend",
            "Should we optimize for speed or add more features?",
            "The UI design needs to be mobile-first or desktop-first",
            "Agent A suggests approach X while Agent B recommends approach Y",
            "Just a normal development task without conflicts"
        ]
        
        for context in test_contexts:
            should_trigger, conflict_type, reason = should_trigger_democracy(context)
            print(f"Context: '{context[:50]}...'")
            print(f"  Trigger Democracy: {should_trigger} | Type: {conflict_type} | Reason: {reason}")
        
    else:
        print("ERROR: Default LLM could NOT be initialized in agents.py.")
        
    print("\n=== Democratic Agent System Ready for Collective Intelligence! ===")