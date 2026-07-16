import pytest
from src.services.llm_router import LLMRouter

@pytest.mark.unit
def test_llm_router_fallback(monkeypatch):
    router = LLMRouter()
    
    async def mock_completion(*args, **kwargs):
        if kwargs.get("model") == "groq/llama-3.3-70b-versatile":
            raise Exception("Groq failed")
        class MockChoice:
            class MockMessage:
                content = "Fallback answer"
            message = MockMessage()
        class MockResponse:
            choices = [MockChoice()]
        return MockResponse()
        
    monkeypatch.setattr("src.services.llm_router.acompletion", mock_completion)
    
    ans = router.generate(prompt="Test")
    assert ans == "Fallback answer"
