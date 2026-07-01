import pytest
from interfaces.base_adapter import BaseChannelAdapter

def test_cannot_instantiate_base_adapter():
    with pytest.raises(TypeError):
        # BaseChannelAdapter is abstract and should raise TypeError on direct instantiation
        BaseChannelAdapter()

def test_subclass_instantiation():
    class MockAdapter(BaseChannelAdapter):
        async def send_message(self, chat_id: str, text: str, parse_mode = None):
            return {"status": "sent", "chat_id": chat_id, "text": text}
            
        async def receive_message(self, message_payload):
            return {"parsed": True, "payload": message_payload}
            
    adapter = MockAdapter()
    assert adapter is not None
