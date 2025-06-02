from ..modules.chatbot_utils import respond, bluetooth_prompt, agent_output_format, agent_system_prompt
from ..modules.agent_tool.func_call_llm import *

from flask import Blueprint, request, jsonify

chatbot_bp = Blueprint('chatbot', __name__)

# Gemma 3 inference
@chatbot_bp.route("/gemma3", methods = ["GET", "POST"])
def gemma3():
    """
    POST message and chat session log to Server to process using Gemma 3 models.\n
    The data shall be in this format: {"message": str, "history": [[message, answer], [message, answer], ...]}.\n
    If everything goes well, the function will send a JSON in format: {"answer": str}, 200.\n
    """
    if request.method == "POST":
        # Catch error:
        try:
            # Get data
            data = request.get_json()
            message = data.get("message")
            # history = data.get("history")
            history = []

            # Pass the user input together with output settings to get_chat_response method.
            results = llama_cpp_agent.get_chat_response(message, structured_output_settings=output_settings)

            # Get context from function calling
            if type(results) is not str: # To avoid error when the model fail to parse the JSON
                context = ""
                for result in results:
                    context += f"\n## Function: {result['function']}\n"
                    context += result['return_value']
            else:
                context = "Error in parsing JSON."

            # Models
            prompt = agent_output_format.format(context = context, user_input = message)
            answer = respond(message = prompt, history = history, model = "gemma-3-1b-it-Q8_0.gguf", system_message = agent_system_prompt)

            return jsonify({
                "message": answer,
                "role": "assistant",
                }), 200
        except:
            return jsonify({
                "message": "There was some error in the Gemma 3 Chatbot (Sever-side error)."
            }), 500
    return jsonify({"error": "Wrong method! This URL is only for POST method"}), 404