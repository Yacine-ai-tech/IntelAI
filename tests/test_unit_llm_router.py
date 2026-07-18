import pytest
from src.services.llm_router import llm_call_sync

@pytest.mark.unit
def test_llm_router_fallback(monkeypatch):
    def mock_completion(*args, **kwargs):
        class MockChoice:
            class MockMessage:
                content = "Fallback answer"
            message = MockMessage()
        class MockResponse:
            choices = [MockChoice()]
        return MockResponse()
        
    monkeypatch.setattr("src.services.llm_router.completion", mock_completion)
    
    ans = llm_call_sync([{"role": "user", "content": "Test"}])
    assert ans.choices[0].message.content == "Fallback answer"
