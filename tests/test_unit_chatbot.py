import pytest
from src.services.omnismart_chatbot import PersonaRouter

@pytest.mark.unit
def test_chatbot_routing(monkeypatch):
    class DummyRetriever:
        def retrieve(self, query):
            return ["Dummy context"]
    
    # Mock Litellm to avoid real API calls
    async def mock_completion(*args, **kwargs):
        class MockChoice:
            class MockMessage:
                content = "Mocked answer"
            message = MockMessage()
        class MockResponse:
            choices = [MockChoice()]
        return MockResponse()
    
    monkeypatch.setattr("src.services.omnismart_chatbot.acompletion", mock_completion)
    
    router = PersonaRouter(retriever=DummyRetriever())
    for persona in router.personas.keys():
        ans = router.route("What is our status?", persona_id=persona, user_id="test_user")
        assert ans is not None
        assert "response" in ans
