%%capture
# @title Prompt Manager

# prompt_manager.py: Module to manage loading and composing prompt templates from Google Docs.

from typing import List, Dict, Any
from jinja2 import Environment, BaseLoader
import yaml
import json

class PromptManager:
    """
    The PromptManager class handles loading and rendering prompt templates from Google Docs.
    It uses Jinja2 templates to render prompts with provided context variables.
    """

    def __init__(self):
        self.env = Environment(loader=BaseLoader())
        self.prompt_cache = {}

    def load_prompt_from_doc(self, doc_url: str) -> str:
        if doc_url in self.prompt_cache:
            return self.prompt_cache[doc_url]
        gdoc = GoogleDoc(doc_url)
        content = gdoc.read_content()
        self.prompt_cache[doc_url] = content
        return content

    def compose_prompt(self, prompt_urls: List[str], template_vars: Dict[str, Any]) -> List[Dict[str, Any]]:
        composed_prompts = []

        for doc_url in prompt_urls:
            content = self.load_prompt_from_doc(doc_url)
            template = self.env.from_string(content)
            prompt_text = template.render(**template_vars)

            try:
                parsed_content = yaml.safe_load(prompt_text.strip())

                if isinstance(parsed_content, dict):
                    parsed_content = [parsed_content]
                elif not isinstance(parsed_content, list):
                    raise ValueError(f"Prompt doc {doc_url} must contain a dictionary or list of dictionaries")

                composed_prompts.extend(parsed_content)

            except yaml.YAMLError as e:
                raise ValueError(f"Failed to parse prompt as YAML in {doc_url}: {str(e)}")

        return composed_prompts

# if __name__ == "__main__":
#     prompt_manager = PromptManager()
#     try:
#         doc_url = "https://docs.google.com/document/d/1jh1XaWHzg-Wrsqn9xGroUtsqjdMUMPRFMdEaor8X84c/edit?tab=t.0"
#         template_vars = {"color": "red"}

#         prompts = prompt_manager.compose_prompt([doc_url], template_vars)
#         print(json.dumps(prompts, indent=2))

#     except Exception as e:
#         print(f"Error occurred: {str(e)}")