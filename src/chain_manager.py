from typing import Dict, Any, List, Callable, Optional
from google.colab import drive
import yaml
import json
from pathlib import Path

DEBUG = False

class ChainManager:
    """Manages execution of chains defined in Google Docs"""

    STEP_FUNCTIONS: Dict[str, Callable] = {}

    @classmethod
    def register_step_function(cls, name: str):
        def decorator(func):
            cls.STEP_FUNCTIONS[name] = func
            return func
        return decorator

    def __init__(self, debug: bool = False):
        self.gdoc = None
        self.debug = debug
        self.prompt_manager = PromptManager()
        self.llm_provider = AnthropicProvider()
        self.steps = []
        self.context = {}

    def load_chain(self, doc_url: str):
        """Load chain configuration from Google Doc URL"""
        self.gdoc = GoogleDoc(doc_url)
        content = self.gdoc.read_content()

        try:
            config = yaml.safe_load(content)
            if DEBUG:
                print(json.dumps(config, indent=2))
            self.name = config.get('name', 'unnamed_chain')
            self.description = config.get('description', '')

            for step_config in config['steps']:
                if step_config['step_function'] not in self.STEP_FUNCTIONS:
                    raise ValueError(f"Unknown step function: {step_config['step_function']}")

                # Extract URLs from prompt templates if they exist
                prompt_templates = step_config.get('prompt_templates', [])
                urls = []
                if isinstance(prompt_templates, list):
                    for template in prompt_templates:
                        if isinstance(template, dict):
                            if 'url' not in template:
                                raise ValueError(f"Missing 'url' key in prompt template for step {step_config['name']}")
                            urls.append(template['url'])

                self.steps.append({
                    'name': step_config['name'],
                    'input_key': step_config.get('input_key'),
                    'output_key': step_config.get('output_key'),
                    'step_function': step_config['step_function'],
                    'prompt_templates': urls
                })

        except Exception as e:
            raise ValueError(f"Error loading chain configuration: {str(e)}")

    def get_context(self) -> Dict[str, Any]:
        return self.context

    def add_to_context(self, key: str, value: Any):
        self.context[key] = value

    def execute(self) -> Dict[str, Any]:
        for step in self.steps:
            func = self.STEP_FUNCTIONS[step['step_function']]
            if DEBUG:
                print(f"Executing step: {step['name']}")
                print(f"Input key: {step['input_key']}")
                print(f"Output key: {step['output_key']}")
                print(f"Step function: {step['step_function']}")
                print(f"Prompt templates: {step['prompt_templates']}")
            result = func(
                chain=self,
                prompt_templates=step.get('prompt_templates', []),
                debug=self.debug
            )

            if step.get('output_key'):
                self.add_to_context(step['output_key'], result)

        return self.context

@ChainManager.register_step_function("process_with_llm")
def process_with_llm(
    chain: Any,
    prompt_templates: List[str] = None,
    debug: bool = False
) -> str:
    context = chain.get_context()
    composed_prompts = chain.prompt_manager.compose_prompt(prompt_templates, context)
    return chain.llm_provider.process_prompt(composed_prompts)

if __name__ == "__main__":
    chain_manager = ChainManager(debug=True)

    try:
        doc_url = "https://docs.google.com/document/d/1qbCRUQtHObwKKRi53FVg3a1SFLjfOLVjIMlr992KWw4/edit?tab=t.0"
        chain_manager.load_chain(doc_url)
        print(f"Loaded chain: {chain_manager.name}")
        print(f"Description: {chain_manager.description}")
        print("\nExecuting chain...")

        chain_manager.add_to_context("text_to_analyze", "Artificial intelligence has transformed numerous industries in recent years. From healthcare to finance, AI systems are automating processes, improving decision-making, and uncovering insights from vast amounts of data. While concerns about AI safety and ethics persist, the technology continues to advance rapidly. Organizations must carefully balance innovation with responsible development practices to ensure AI benefits society as a whole.")
        chain_manager.add_to_context("tone", "Academic")

        # print(json.dumps(chain_manager.get_context(), indent=2))

        result = chain_manager.execute()
        print("\nExecution completed. Final context:")
        print(json.dumps(result, indent=2))

    except Exception as e:
        print(f"Error occurred: {str(e)}")