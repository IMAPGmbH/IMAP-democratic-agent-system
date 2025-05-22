#!/usr/bin/env python3
"""Minimal test für democracy tools"""

import os
from dotenv import load_dotenv

load_dotenv()

# Test 1: Können wir die Tools importieren?
try:
    print("Testing imports...")
    from tools.team_voting_tool import trigger_democratic_decision_tool
    print("✅ team_voting_tool imported")
    
    from agents import project_manager_agent
    print("✅ agents imported")
    
    print("\nTesting tool call...")
    result = trigger_democratic_decision_tool._run(
        conflict_type="architecture_decision",
        trigger_reason="Test",
        context="Test context",
        participating_agents=["Developer", "Tester"]
    )
    print(f"✅ Tool result: {result[:100]}...")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()