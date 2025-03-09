import yaml
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()


class Models:
    def __init__(self, model_name, temperature: float = 0):
        """
        Initialize the LangChain OpenAI model with parameters from a secrets file.

        Args:
            model_name (str): Name of the model, for now only openai ones
            temperature (float): Sampling temperature, affects the creativity of the output.
            max_tokens (int): Maximum number of tokens in the generated response.
        """
        self.temperature = temperature
        self.api_key = None
        self.model = None
        self.model_name = model_name
        self.initialize_model()

    def initialize_model(self):
        """
        Initializes the LangChain OpenAI model instance.
        """
        self.model = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            max_retries=3
        )

