#!/usr/bin/env python3
import asyncio
from interfaces.telegram_interface import TelegramInterface
from pydantic import BaseModel
from typing import Optional, AsyncGenerator

# Mock NinaConfig for testing
class MockNinaConfig(BaseModel):
    telegram_bot_token: str = "placeholder"
    telegram_chat_id: str = "placeholder"
    ollama_host: str = "http://localhost:11434"
    api_secret_key: Optional[str] = None
    flood_window_s: int = 60
    flood_max_messages: int = 20
    session_max_turns: int = 10

# Mock NinaOS for testing
class MockNinaOS:
    def __init__(self):
        self.router = MockRouter()
        self.system_prompt = "You are a helpful assistant."
        self.tools = {"shell": MockShellTool()}
        self.memory = MockMemory()
        self.pipeline = MockPipeline()
        self.agent = MockAgent()
        self.idle_loop = MockIdleLoop()

    async def get_status(self):
        return "Mock NinaOS Status"

class MockRouter:
    def get_status(self):
        return "Mock Router Status"

    def get_health_summary(self):
        return "Mock Health Summary"

    async def route(self, prompt, messages, task, force_local=False, stream=False):
        if stream:
            async def mock_stream():
                for chunk in ["Mock ", "streaming ", "response."]:
                    yield chunk
            return mock_stream()
        return "Mock response"

class MockShellTool:
    async def run(self, cmd):
        return f"Mock shell output for: {cmd}"

class MockMemory:
    async def kb_add_entry(self, tags, text):
        pass

    async def kb_search(self, query):
        return []

    async def backup(self):
        return "/tmp/mock_backup.json"

    async def wipe_and_reinitialize(self):
        pass

    async def goal_add(self, text):
        return "mock_goal_id"

    async def goal_done(self, goal_id):
        pass

    async def goal_list(self):
        return []

class MockPipeline:
    async def handle_command(self, cmd, arg):
        return f"Mock pipeline output for: {cmd} {arg}"

class MockAgent:
    async def run(self, prompt, task, session_history):
        return f"Mock agent output for: {prompt}"

class MockIdleLoop:
    def record_user_message(self):
        pass

async def test_telegram():
    nina_os = MockNinaOS()
    telegram = TelegramInterface(MockNinaConfig(), nina_os)
    
    # Mock the Telegram API to avoid requiring a real token
    telegram._app = MockTelegramApp()
    
    print("TelegramInterface initialized. Testing for 100 minutes...")
    
    # Simulate user interactions every 10 seconds
    for i in range(600):  # 600 requests * 10 seconds = 6000 seconds (100 minutes)
        try:
            # Simulate a command
            if i % 5 == 0:
                await telegram._handle_command(MockUpdate(), "status", "")
            elif i % 5 == 1:
                await telegram._handle_command(MockUpdate(), "ask", "What is the meaning of life?")
            elif i % 5 == 2:
                await telegram._handle_command(MockUpdate(), "opencode", "Add docstrings to tools/finance.py")
            elif i % 5 == 3:
                await telegram._handle_command(MockUpdate(), "ndev", "")
            else:
                await telegram._handle_command(MockUpdate(), "help", "")
            print(f"Interaction {i}: Success")
        except Exception as e:
            print(f"Interaction {i}: Failed - {e}")
        await asyncio.sleep(10)
    
    await telegram.stop()

# Mock Telegram classes for testing
class MockUpdate:
    def __init__(self):
        self.message = MockMessage()
        self.effective_user = MockUser()
        self.effective_chat = MockChat()

class MockMessage:
    def __init__(self):
        self.text = "Test message"
        self.document = None

    async def reply_text(self, text, **kwargs):
        print(f"Mock reply: {text}")

    async def edit_text(self, text, **kwargs):
        print(f"Mock edit: {text}")

class MockUser:
    def __init__(self):
        self.id = "placeholder"

class MockChat:
    def __init__(self):
        self.id = "placeholder"

class MockTelegramApp:
    async def initialize(self):
        pass

    async def start(self):
        pass

    async def stop(self):
        pass

    async def shutdown(self):
        pass

if __name__ == "__main__":
    asyncio.run(test_telegram())