import json
import asyncio
import os
from src.services.omnismart_chatbot import PersonaRouter

async def main():
    print("Starting RAG Evaluation...")
    router = PersonaRouter()
    
    eval_file = os.path.join(os.path.dirname(__file__), "rag_eval.jsonl")
    results = []
    
    with open(eval_file, "r") as f:
        for line in f:
            if not line.strip(): continue
            data = json.loads(line)
            query = data["query"]
            expected = data["expected"]
            persona = data["persona"]
            
            print(f"Evaluating query: '{query}' for persona: {persona}")
            # Mock or run real if configured
            try:
                response = router.route(query, persona_id=persona, user_id="eval_user")
                answer = response.get("response", "").lower()
                passed = expected.lower() in answer
                results.append({"query": query, "passed": passed})
            except Exception as e:
                print(f"Error evaluating {query}: {e}")
                results.append({"query": query, "passed": False})
                
    passed_count = sum(1 for r in results if r["passed"])
    print(f"Evaluation Complete! Score: {passed_count}/{len(results)}")

if __name__ == "__main__":
    asyncio.run(main())
