# Import the LlmStructuredOutputSettings
from llama_cpp_agent.llm_output_settings import LlmStructuredOutputSettings
from llama_cpp_agent import LlamaCppAgent
from llama_cpp_agent.providers import LlamaCppPythonProvider
from llama_cpp_agent.llm_output_settings import LlmStructuredOutputSettings
from llama_cpp_agent import MessagesFormatterType
from llama_cpp import Llama

import os
from app.modules.agent_tool.tools import search_func, weather_func, wikipedia_func, gmail_func
from app.modules.chatbot_utils import respond

# Get model instance
model_path = os.path.join(os.getcwd(), "app\llm_models\Llama-3.2-1B-Instruct-Q8_0.gguf")
llm = Llama(
    model_path=model_path,
    n_batch=1024, n_threads=10, n_gpu_layers=40
)

# Get provider
provider = LlamaCppPythonProvider(llm)

# Now let's create an instance of the LlmStructuredOutput class by calling the `from_functions` function of it and passing it a list of functions.
func_list = [search_func, weather_func, wikipedia_func, gmail_func]
output_settings = LlmStructuredOutputSettings.from_functions(func_list, allow_parallel_function_calling=True)

# Create a LlamaCppAgent instance as before, including a system message with information about the tools available for the LLM agent.
llama_cpp_agent = LlamaCppAgent(
    provider,
    debug_output=True,
    system_prompt=f"You are an advanced AI, tasked to assist the user by calling functions in JSON format.",
    predefined_messages_formatter_type=MessagesFormatterType.CHATML,
)