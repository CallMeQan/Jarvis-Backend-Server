from ..modules.chatbot_utils import respond, agent_output_format, agent_system_prompt, bluetooth_prompt

from flask import Blueprint, request, jsonify
import json

chatbot_bp = Blueprint('chatbot', __name__)

# Only a simple chatbot
@chatbot_bp.route("/vanilla", methods = ["GET", "POST"])
def vanilla():
    """
    POST message and chat session log to Server to process using a Gemma 3 chatbot model.\n
    The data shall be in this format: {"message": str, "history": [[message, answer], [message, answer], ...]}.\n
    If everything goes well, the function will send a JSON in format: {"answer": str, "role": str}, 200.\n
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
            answer = respond(message, history = history)

            return jsonify({
                "message": answer,
                "role": "assistant",
                }), 200

        except Exception as e:
            return jsonify({
                "message": f"There was some error in the Gemma 3 Chatbot (Sever-side error).: {e}",
                "role": "assistant"
            }), 200
    return jsonify({"error": "Wrong method! This URL is only for POST method"}), 404

# function_call_chatbot
@chatbot_bp.route("/function_call_chatbot", methods = ["GET", "POST"])
def function_call_chatbot():
    """
    POST message and chat session log to Server to process using a Llama 3.2 function calling model and Gemma 3 chatbot model.\n
    The data shall be in this format: {"message": str, "history": [[message, answer], [message, answer], ...]}.\n
    If everything goes well, the function will send a JSON in format: {"answer": str, "role": str}, 200.\n
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
            results = respond(message, use_func_call=True)

            # Get context from function calling
            if type(results) is not str: # To avoid error when the model fail to parse the JSON
                context = ""
                for result in results:
                    context += f"\n## Function: {result['function']}\n"
                    context += result['return_value']
            else:
                context = "No context - There is an error in parsing JSON."

            # Models
            prompt = agent_output_format.format(context = context, user_input = message)
            answer = respond(message = prompt, history = history, model = "gemma-3-1b-it-Q8_0.gguf", system_message = agent_system_prompt)

            return jsonify({
                "message": answer,
                "role": "assistant",
                }), 200
        except:
            return jsonify({
                "message": "There was some error in the Gemma 3 Chatbot (Sever-side error).",
                "role": "assistant"
            }), 200
    return jsonify({"error": "Wrong method! This URL is only for POST method"}), 404

# Bluetooth processor using Llama 3.2 1B Instruct finetuned with GRPO
@chatbot_bp.route("/bluetooth_processor", methods = ["GET", "POST"])
def bluetooth_processor():
    """
    POST message and chat session log to Server to process command using finetuned Llama 3.2 1B model.\n
    The data shall be in this format: {"message": str, "history": []}.\n
    If everything goes well, the function will send a JSON in format: {"answer": str, "role": str}, 200.\n
    """
    if request.method == "POST":
        # Catch error:
        try:
            # Get data
            data = request.get_json()
            message = data.get("message")

            # Loop that let model try x times
            tries = 0
            while True:
                try:
                    answer = ""
                    commands = respond(message = message, history = [], model = "Llama-3.2-1B-Instruct-GRPO-GGUF.gguf", system_message = bluetooth_prompt)
                    commands = json.loads(commands)
                    for command in commands:
                        answer += f"{command['signal']},{command['color']};"
                    break
                except:
                    tries += 1
                    if tries == 3:
                        return jsonify({
                            "message": "Failed to get the command!",
                            "role": "assistant"
                        }), 200
            return jsonify({
                "message": answer,
                "role": "assistant",
                }), 200
        except:
            return jsonify({
                "message": "There was some error in the Bluetooth processor (Sever-side error).",
                "role": "assistant"
            }), 200
    return jsonify({"error": "Wrong method! This URL is only for POST method"}), 404