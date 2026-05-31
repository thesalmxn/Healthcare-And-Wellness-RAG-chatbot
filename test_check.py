#!/usr/bin/env python3
"""
Quick test script to verify the system before full build
"""

import os
import sys
from pathlib import Path

def check_setup():
    """Verify all prerequisites are in place"""
    print("🔍 Checking setup...\n")
    
    issues = []
    
    # Check data directory
    data_dir = Path("data/raw_pdfs")
    if not data_dir.exists():
        issues.append(f"❌ Data directory not found: {data_dir}")
    else:
        files = list(data_dir.glob("*.pdf")) + list(data_dir.glob("*.docx"))
        print(f"✅ Data directory found: {len(files)} files")
    
    # Check if vector store exists
    vector_dir = Path("vector_store")
    if vector_dir.exists():
        print(f"⚠️  Vector store already exists - will be overwritten")
    else:
        print(f"✅ Vector store directory ready")
    
    # Check Ollama
    try:
        import subprocess
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if 'llama3.1:8b' in result.stdout:
            print("✅ Ollama llama3.1:8b available")
        else:
            issues.append("❌ llama3.1:8b model not found in Ollama")
            
        if 'nomic-embed-text' in result.stdout:
            print("✅ Ollama nomic-embed-text available")
        else:
            issues.append("❌ nomic-embed-text model not found in Ollama")
    except:
        issues.append("❌ Ollama not installed or not running")
    
    # Check Python packages
    required = ['deep_translator', 'langchain', 'faiss', 'streamlit']
    for pkg in required:
        try:
            __import__(pkg.replace('-', '_'))
            print(f"✅ {pkg} installed")
        except:
            issues.append(f"❌ {pkg} not installed")
    
    print()
    
    if issues:
        print("⚠️  ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("✅ All checks passed!")
        return True

def show_next_steps():
    """Show what to do next"""
    print("\n" + "="*70)
    print("📋 NEXT STEPS")
    print("="*70)
    print("""
1. TEST BUILD (Recommended - ~5-10 minutes):
   python src/ingest/build_index.py --test
   
   This will:
   - Process 5 documents
   - Create ~30-50 chunks
   - Translate to English
   - Build test index
   
2. TEST CHAT INTERFACE:
   streamlit run app.py
   
   Try queries like:
   - "Τι βοηθάει τον ύπνο;" (Greek)
   - "What wellness practices help with sleep?" (English)
   
3. IF TEST WORKS WELL, RUN FULL BUILD (~2-3 hours):
   python src/ingest/build_index.py
   
   This will process all 350 documents (~4000-5000 chunks)
""")

if __name__ == "__main__":
    print("="*70)
    print("🌿 HEALTH & WELLNESS RAG - PRE-FLIGHT CHECK")
    print("="*70)
    print()
    
    if check_setup():
        show_next_steps()
    else:
        print("\n⚠️  Please fix the issues above before proceeding.")
        sys.exit(1)