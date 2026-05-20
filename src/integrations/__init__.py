"""
Unified Integrations Module — Single point for all external system connectivity.

This module provides a centralized, efficient integration system with:
- Zero duplication of service logic
- Unified error handling & retry logic
- Connection pooling and resource management
- Event-driven architecture for webhooks
- Comprehensive health monitoring

SUPPORTED INTEGRATIONS:
1. N8N — Workflow automation
2. Gmail — Email management & automation
3. Google Sheets — Spreadsheet data sync
4. Tavily — Web search & research
5. Voice/Whisper — Audio transcription
6. TTS — Text-to-speech (gTTS, ElevenLabs, Azure)
7. Camera — Webcam & IP camera access

USAGE:
    from src.integrations import get_dispatcher
    
    dispatcher = await get_dispatcher()
    
    # Access specific integration
    gmail = dispatcher.get_integration(IntegrationTypeEnum.GMAIL)
    emails = await gmail.fetch_emails("user@example.com")
    
    # Register event handlers
    async def on_email_received(event):
        print(f"Email received: {event.payload}")
    
    dispatcher.register_event_handler(
        IntegrationEventTypeEnum.MESSAGE_RECEIVED,
        on_email_received
    )
"""

from src.integrations.dispatcher import (
    BaseIntegration,
    GmailIntegration,
    IntegrationDispatcher,
    IntegrationEvent,
    IntegrationEventTypeEnum,
    IntegrationTypeEnum,
    N8NIntegration,
    SheetsIntegration,
    TavilyIntegration,
    TTSIntegration,
    VoiceIntegration,
    get_dispatcher,
    shutdown_dispatcher,
)

__all__ = [
    # Dispatcher
    "IntegrationDispatcher",
    "get_dispatcher",
    "shutdown_dispatcher",
    # Enums
    "IntegrationTypeEnum",
    "IntegrationEventTypeEnum",
    # Event
    "IntegrationEvent",
    # Base
    "BaseIntegration",
    # Implementations
    "N8NIntegration",
    "GmailIntegration",
    "SheetsIntegration",
    "TavilyIntegration",
    "VoiceIntegration",
    "TTSIntegration",
]

