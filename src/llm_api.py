from abc import ABC, abstractmethod
from typing import Dict, Any, List
import anthropic
import json
import os


DEBUG = True
os.environ["ANTHROPIC_API_KEY"] = LLM_API_KEY

class LLMProvider(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def convert_to_messages(self, prompt_dicts: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], str]:
        pass

    @abstractmethod
    def generate(self, messages: tuple[List[Dict[str, Any]], str]) -> Any:
        pass

    @abstractmethod
    def parse_response(self, response: Any) -> str:
        pass

    def process_prompt(self, prompt_dicts: List[Dict[str, Any]]) -> str:
        messages_and_system = self.convert_to_messages(prompt_dicts)
        response = self.generate(messages_and_system)
        return self.parse_response(response)


class AnthropicProvider(LLMProvider):
    def __init__(self, model: str = "claude-3-5-sonnet-20240620"):
        super().__init__()
        self.client = anthropic.Anthropic()
        self.model = model

    def extract_system_message(self, messages: List[Dict[str, Any]]) -> tuple[str, List[Dict[str, Any]]]:
        system_messages = []
        other_messages = []

        for message in messages:
            if message['role'] == 'system':
                system_messages.append(message['content'])
            else:
                other_messages.append(message)

        system_message = ' '.join(system_messages)
        return system_message, other_messages

    def convert_to_messages(self, prompt_dicts: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], str]:
        system_message, other_messages = self.extract_system_message(prompt_dicts)
        converted_messages = [
            {
                "role": msg.get("role", "user"),
                "content": msg["content"]
            }
            for msg in other_messages
        ]
        return converted_messages, system_message

    def generate(self, messages_and_system: tuple[List[Dict[str, Any]], str]) -> Any:
        converted_messages, system_message = messages_and_system
        request_args = {
            "model": self.model,
            "messages": converted_messages,
            "max_tokens": 4096,
            "temperature": 0.0
        }

        if system_message:
            request_args["system"] = system_message
        if DEBUG:
          print("Message Chain:")
          print(json.dumps(converted_messages, indent=2))
        response = self.client.messages.create(**request_args)
        if DEBUG:
          print("Response:")
          print(response)
        return response

    def parse_response(self, response: Any) -> str:
        return response.content[0].text

if __name__ == "__main__":
    provider = AnthropicProvider()
    prompt_dicts = [
        {
            "role": "system",
            "content": "You are a helpful AI assistant. Be concise."
        },
        {
            "role": "user",
            "content": "Tell me a short story about a robot."
        }
    ]
    response = provider.process_prompt(prompt_dicts)
    print(response)