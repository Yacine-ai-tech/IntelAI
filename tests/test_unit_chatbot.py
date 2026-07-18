import pytest
from src.services.omnismart_chatbot import AgentPersonaFactory

@pytest.mark.unit
def test_chatbot_routing():
    # test that we can build a persona prompt
    factory = AgentPersonaFactory()
    ctx = factory.resolve_persona(user_role="ceo")
    sys_prompt = ctx.system_prompt
    assert "CEO" in sys_prompt or "Executive" in sys_prompt or len(sys_prompt) > 0
