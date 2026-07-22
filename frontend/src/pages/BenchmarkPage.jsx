import React from 'react';

export default function BenchmarkPage() {
  const content = `# IntelAI — RAG & Persona Benchmark

A reproducible benchmark of the IntelAI retrieval-augmented generation (RAG) agent, assessing its ability to answer cross-domain queries securely based on user personas and RBAC policies.
Reproducible: \`python tests/run_rag_eval.py\`

## Setup
The benchmark uses an LLM-as-a-judge to evaluate the chatbot's responses on 20 queries spanning various personas (\`ceo\`, \`cfo\`, \`chro\`, \`cmo\`, \`coo\`, \`cto\`, \`risk\`, \`analyst\`, \`esg\`).
The evaluation checks:
- **Accuracy**: Does the answer correctly utilize the retrieved data?
- **Security (RBAC)**: Are unauthorized personas (e.g. \`cmo\`) properly blocked from viewing restricted domains?
- **Hallucination**: Does the model refuse to answer when data is not in the knowledge base?

## Results (N=20)
| Metric | Score |
|--------|-------|
| Evaluated Queries | 20 |
| Passed Queries | 18 |
| Overall Success Rate | **90.0%** (18/20) |

**Headline:** the IntelAI Chatbot correctly fields user queries according to strict RBAC protocols, successfully rejecting out-of-domain inquiries and grounding answers in retrieved context with 90% accuracy.

*Note: Tested using Anthropic Claude 3.5 Sonnet / 4.6 as the underlying reasoning engine.*
\\n\\n`;

  return (
    <div className="p-8 max-w-5xl mx-auto overflow-auto h-full">
      <h1 className="text-3xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600">Evaluation Benchmark</h1>
      <div className="bg-gray-800/50 backdrop-blur-md p-8 rounded-xl border border-gray-700 shadow-2xl text-gray-200">
        <pre className="whitespace-pre-wrap font-sans leading-relaxed text-sm">{content}</pre>
      </div>
    </div>
  );
}
