from ..modules.chatbot_utils import respond

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
        # TODO: Check authentication

        # Get data
        message = request.form.get("message")
        history = request.form.get("history")

        # Models
        answer = respond(message = message, history = history, model = "gemma-3-1b-it-Q8_0.gguf")

        return jsonify({"answer": answer}), 200
    return jsonify({"error": "Wrong method! This URL is only for POST method"}), 404