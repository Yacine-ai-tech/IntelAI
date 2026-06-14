# omnismart-personas

Role-based, **data-scoped** LLM persona templates + router for production analytics
copilots. The pattern behind IntelAI's 9-persona RAG copilot, extracted as a tiny,
zero-dependency, pure-Python library.

A *persona* pairs a **system prompt** with a **data-access scope** (which business
domains it may see) and a sampling temperature — so the same retrieval system can answer
through different role-conditioned prompts *and* data filters ("persona-routed RAG").

## Install

```bash
pip install omnismart-personas
```

## Use

```python
from omnismart_personas import persona_for_role, scope_records, build_rag_prompt

persona = persona_for_role("cfo")          # → CFO persona (scope: Finance, Growth)
persona.can_access("People")               # False — out of scope

rows = [
    {"category": "Finance", "metric": "gross_margin", "value": 0.42},
    {"category": "People",  "metric": "headcount",    "value": 220},
]
visible = scope_records(persona, rows)     # drops the People row

prompt = build_rag_prompt(
    persona,
    "What drove the Q1 gross-margin change?",
    [f"{r['metric']}={r['value']}" for r in visible],
    language="en",
)
# → send `prompt` to any LLM
```

## API

- `list_personas()` → the 9 persona keys
- `get_persona(name)` / `persona_for_role(role)` → a `Persona`
- `Persona(name, display_name, system_prompt, allowed_tools, data_access, temperature)` —
  immutable; `.can_access(domain)`
- `scope_records(persona, records, domain_key="category")` → records in scope
- `build_system_prompt(persona, *, language="en", extra=None)`
- `build_rag_prompt(persona, query, snippets, *, language="en")`

Personas: `ceo, cfo, cto, coo, chro, esg, risk, analyst, general`.

## LangChain

Use the personas in any LangChain RAG chain — `pip install "omnismart-personas[langchain]"`:

```python
from omnismart_personas import persona_for_role
from omnismart_personas.langchain import persona_chat_prompt, persona_retriever_filter
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

persona = persona_for_role("cfo")
prompt = persona_chat_prompt(persona)               # system = scope; {context} + {question}
chain = prompt | ChatOpenAI(model="gpt-4o-mini") | StrOutputParser()

docs = persona_retriever_filter(persona, retriever.invoke(q))   # RBAC on retrieved docs
answer = chain.invoke({"context": "\n".join(d.page_content for d in docs), "question": q})
```

`persona_retriever_filter` drops `Document`s whose `metadata["category"]` is outside the
persona's `data_access` scope — the same role boundaries, enforced in your LangChain pipeline.

## Test

```bash
pip install -e ".[test]" && pytest
```

MIT licensed. Part of the [IntelAI](https://github.com/Yacine-ai-tech/IntelAI) project.
