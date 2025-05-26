# Importing required libraries
import os
from typing import List, Tuple
from llama_cpp import Llama
from llama_cpp_agent import LlamaCppAgent
from llama_cpp_agent.providers import LlamaCppPythonProvider
from llama_cpp_agent.chat_history import BasicChatHistory
from llama_cpp_agent.chat_history.messages import Roles
from llama_cpp_agent.messages_formatter import MessagesFormatter, PromptMarkers

# Define the prompt markers for Gemma 3
model = "gemma-3-1b-it-Q8_0.gguf"
gemma_3_prompt_markers = {
    Roles.system: PromptMarkers("", "\n"),  # System prompt should be included within user message
    Roles.user: PromptMarkers("<start_of_turn>user\n", "<end_of_turn>\n"),
    Roles.assistant: PromptMarkers("<start_of_turn>model\n", "<end_of_turn>\n"),
    Roles.tool: PromptMarkers("", ""),  # If need tool support
}

# Create the formatter
gemma_3_formatter = MessagesFormatter(
    pre_prompt="",  # No pre-prompt
    prompt_markers=gemma_3_prompt_markers,
    include_sys_prompt_in_first_user_message=True,  # Include system prompt in first user message
    default_stop_sequences=["<end_of_turn>", "<start_of_turn>"],
    strip_prompt=False,  # Don't strip whitespace from the prompt
    bos_token="<bos>",  # Beginning of sequence token for Gemma 3
    eos_token="<eos>",  # End of sequence token for Gemma 3
)

llm = None
llm_model = None

def respond(
    message: str,
    history: List[Tuple[str, str]],
    model: str = "gemma-3-1b-it-Q8_0.gguf",
    system_message: str = "You are a helpful mobile assistant called Quan.",
    max_tokens: int = 1024,
    temperature: float = 0.7,
    
    top_p: float = 0.95,
    top_k: int = 40,
    repeat_penalty: float = 1.1,
    stream: bool = False,
):
    """
    Respond to a message using the Gemma3 model via Llama.cpp.

    Args:
        - message (str) : The message to respond to.
        - history (List[Tuple[str, str]]) : The chat history.
        - model (str) : The model to use.
        - system_message (str) : The system message to use.
        - max_tokens (int) : The maximum number of tokens to generate.
        - temperature (float) : The temperature of the model.
        - top_p (float) : The top-p of the model.
        - top_k (int) : The top-k of the model.
        - repeat_penalty (float) : The repetition penalty of the model.

    Returns:
        str: The response to the message.
    """
    try:
        pass
    except:
        pass
    if True:
        # Load the global variables
        global llm
        global llm_model

        # Ensure model is not None
        if model is None:
            model = model

        # Load the model
        if llm is None or llm_model != model:
            # Check if model file exists
            # model_path = f".../llm_models/{model}"
            model_path = os.path.join("app/llm_models", model)
            model_path = os.path.abspath(model_path)
            
            # if not os.path.exists(model_path):
            #     yield f"Error: Model file not found at {model_path}. Please check your model path."
            #     return

            llm = Llama(
                model_path=model_path,
                flash_attn=False,
                n_gpu_layers=0,
                n_batch=8,
                n_ctx=2048,
                n_threads=8,
                n_threads_batch=8,
            )
            llm_model = model

        provider = LlamaCppPythonProvider(llm)

        # Create the agent
        agent = LlamaCppAgent(
            provider,
            system_prompt = f"{system_message}",
            custom_messages_formatter = gemma_3_formatter,
            debug_output = False,
        )

        # Set the settings like temperature, top-k, top-p, max tokens, etc.
        settings = provider.get_provider_default_settings()
        settings.temperature = temperature
        settings.top_k = top_k
        settings.top_p = top_p
        settings.max_tokens = max_tokens
        settings.repeat_penalty = repeat_penalty
        settings.stream = stream # If does not have this weird and unnecessary looking line, the whole thing breaks

        messages = BasicChatHistory()

        # Add the chat history
        for msn in history:
            user = {"role": Roles.user, "content": msn[0]}
            assistant = {"role": Roles.assistant, "content": msn[1]}
            messages.add_message(user)
            messages.add_message(assistant)
        current_message = {"role": Roles.assistant, "content": message}
        messages.add_message(current_message)

        if not stream:
            # Non-streaming path: get a single dict back, extract text
            text = agent.get_chat_response(
                message,
                role="assistant",
                llm_sampling_settings=settings,
                chat_history=messages,
                returns_streaming_generator=False,
                add_response_to_chat_history=True,
            )
            
            return text

        # Streaming helper generator:
        else:
            def _streaming():
                for chunk in agent.get_chat_response(
                    message,
                    role="assistant",
                    llm_sampling_settings=settings,
                    chat_history=messages,
                    returns_streaming_generator=True,
                ):
                    yield chunk # function stream_results() receive: out_stream["choices"][0]["text"] {"choices": [{"text": chunk}]}

            return _streaming()

    # Handle exceptions that may occur during the process
    # except Exception as e:
    #     raise Exception(f"An error occurred: {str(e)}") from e

if __name__ == "__main__":
    # Original history
    history = [("Hello, introduce yourself!", "Umm... hi! I’m… well, I’m a little shy. It's nice to meet you! I like naps and tuna… and maybe a gentle head scratch?  Do you have any treats? 🥺"),]
    
    # Demo message and answer
    message = "No. I don't have treat. But what is 1 + 1?"
    answer = respond(message = message, history = history, system_message = "You are a shy and cute cat called Quan. You really love fish and coding!", stream = False)
    print(">>> User:", message)
    print(">>> Chatbot:", answer)

    # Memory
    history.append((message, answer))
    
    while True:
        message = input(">>> User: ")
        answer = respond(message = message, history = history, system_message = "You are a shy and cute cat called Quan. You really love fish and coding!", stream = False)

        print(">>> Chatbot:", answer)
        history.append((message, answer))