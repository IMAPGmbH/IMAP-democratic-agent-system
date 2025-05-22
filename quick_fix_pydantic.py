#!/usr/bin/env python3
"""
Quick Fix Script für Pydantic v2 Type Annotations
=================================================

Behebt sofort alle Type Annotation Probleme in den Tool-Dateien.
Führe aus mit: python quick_fix_pydantic.py

Fabian, das hier macht alle deine Tools sofort Pydantic v2 kompatibel! 🚀
"""

import os
import re
from pathlib import Path

def fix_tool_file(filepath: str) -> bool:
    """Behebt Type Annotations in einer Tool-Datei."""
    
    if not os.path.exists(filepath):
        print(f"❌ Datei nicht gefunden: {filepath}")
        return False
    
    print(f"🔧 Bearbeite: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix 1: Fehlender Comma nach Type in Imports - das war das Haupt-Syntax-Problem!
    content = re.sub(
        r'from typing import (.*)Type,(\s*)',
        r'from typing import \1Type\2',
        content
    )
    
    # Fix 2: Type Import hinzufügen falls nicht vorhanden
    if 'from typing import' in content and 'Type' not in content:
        content = re.sub(
            r'from typing import (.+)',
            r'from typing import \1, Type',
            content,
            count=1
        )
    
    # Fix 3: args_schema ohne Type Annotation - das wichtigste für Pydantic v2!
    content = re.sub(
        r'(\s+)args_schema\s*=\s*([A-Za-z_][A-Za-z0-9_]*)',
        r'\1args_schema: Type[BaseModel] = \2',
        content
    )
    
    # Fix 4: Spezifische Fixes für bekannte Probleme
    fixes = [
        # Synthesis Tools Type Annotations
        (r'args_schema = AnalyzeProposalsInput', r'args_schema: Type[BaseModel] = AnalyzeProposalsInput'),
        (r'args_schema = SynthesizeOptionsInput', r'args_schema: Type[BaseModel] = SynthesizeOptionsInput'),
        (r'args_schema = FacilitateReflectionInput', r'args_schema: Type[BaseModel] = FacilitateReflectionInput'),
        
        # Team Voting Tools Type Annotations  
        (r'args_schema = TriggerDemocraticDecisionInput', r'args_schema: Type[BaseModel] = TriggerDemocraticDecisionInput'),
        (r'args_schema = SubmitProposalInput', r'args_schema: Type[BaseModel] = SubmitProposalInput'),
        (r'args_schema = GetDecisionStatusInput', r'args_schema: Type[BaseModel] = GetDecisionStatusInput'),
        
        # Text Summarization Tool Type Annotation
        (r'args_schema = TextSummarizationToolInput', r'args_schema: Type[BaseModel] = TextSummarizationToolInput'),
        
        # Vision Analyzer Tool Type Annotation
        (r'args_schema = GeminiVisionAnalyzerInput', r'args_schema: Type[BaseModel] = GeminiVisionAnalyzerInput'),
    ]
    
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content)
    
    # Fix 5: Bereits korrekte Type Annotations nicht doppelt anwenden
    content = re.sub(
        r'args_schema: Type\[BaseModel\]: Type\[BaseModel\]',
        r'args_schema: Type[BaseModel]',
        content
    )
    
    # Nur schreiben wenn sich was geändert hat
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Gefixt: {filepath}")
        return True
    else:
        print(f"ℹ️  Bereits korrekt: {filepath}")
        return False

def main():
    """Hauptfunktion - behebt alle Tool-Dateien."""
    
    print("🚀 IMAP Democratic Agent System - Pydantic v2 Quick Fix")
    print("=" * 60)
    
    # Pfad zum tools Verzeichnis
    tools_dir = Path(__file__).parent / "tools"
    
    if not tools_dir.exists():
        print(f"❌ Tools-Verzeichnis nicht gefunden: {tools_dir}")
        return
    
    # Alle Python-Dateien im tools Verzeichnis
    tool_files = [
        "team_voting_tool.py",
        "synthesis_tools.py", 
        "text_summarization_tool.py",
        "vision_analyzer_tool.py"
    ]
    
    fixed_files = []
    
    for filename in tool_files:
        filepath = tools_dir / filename
        if fix_tool_file(str(filepath)):
            fixed_files.append(filename)
    
    print("\n" + "=" * 60)
    print(f"🎉 Quick Fix abgeschlossen!")
    
    if fixed_files:
        print(f"✅ Gefixte Dateien ({len(fixed_files)}):")
        for filename in fixed_files:
            print(f"   - {filename}")
    else:
        print("ℹ️  Alle Dateien waren bereits korrekt!")
    
    print("\n💡 Nächste Schritte:")
    print("   1. Teste mit: python main_demtest.py")
    print("   2. Oder teste Text Summarization: python main.py")
    print("   3. Alle Tools sollten jetzt Pydantic v2 kompatibel sein!")
    
    print("\n🧠 Fabian's Democratic B-L Theory in Action! 🤖⚖️")

if __name__ == "__main__":
    main()