import json
import asyncio
import os
import sys

from src.services.omnismart_chatbot import get_persona_factory

def main():
    print("Starting RAG Evaluation (Live LLM)...")
    factory = get_persona_factory()
    
    eval_file = os.path.join(os.path.dirname(__file__), "rag_eval.jsonl")
    if not os.path.exists(eval_file):
        print(f"Error: {eval_file} not found")
        sys.exit(1)

    results = []
    
    with open(eval_file, "r") as f:
        for line in f:
            if not line.strip(): continue
            data = json.loads(line)
            query = data["query"]
            expected = data["expected"]
            persona = data["persona"]
            
            print(f"Evaluating query: '{query}' for persona: {persona}")
            try:
                response = factory.chat(message=query, user_role=persona, persona_override=persona)
                answer = response.get("response", "").lower()
                print(f"  Answer: {answer}")
                passed = expected.lower() in answer
                
                print(f"  Passed: {passed}")
                results.append({"query": query, "passed": passed})
            except Exception as e:
                print(f"  Error evaluating {query}: {e}")
                results.append({"query": query, "passed": False})
                
    passed_count = sum(1 for r in results if r["passed"])
    total = len(results)
    
    print("\n--- RESULTS ---")
    print(f"Evaluation Complete! Score: {passed_count}/{total} ({(passed_count/total)*100 if total else 0:.1f}%)")

if __name__ == "__main__":
    main()
