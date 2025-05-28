from ..modules.chatbot_utils import respond, bluetooth_prompt
from ..modules.agent_tool.search_tool import search, lookup_weather
from ..modules.agent_tool.wikipedia_tool import get_wiki_first_paragraph
from ..modules.agent_tool.gmail_tool import send_email

from flask import Blueprint, request, jsonify

chatbot_bp = Blueprint('chatbot', __name__)

# Helping function
def get_command(message: str):
    """
    Find the first command in the message and respond accordingly. A command format: @/command<<query>>.
    Example: "hello@/abc<query1> Jarvis" -> ("helloJarvis", "abc", "query1").

    :message: String message that may contain @/command.
    :return: (String command (without @/) or False if no command, query without command)
    """
    index = message.find("@/")
    if index != -1:
        command = message[index:].split()[0]

        # Take query from message
        query_start = command.find("<")
        query_end = command.find(">")
        print(command)

        # Get message with no command
        '''
        message: "hello @/abc<query1> Jarvis" -> "helloJarvis"
        command: "hello @/abc<query1> Jarvis" -> "abc"
        query: "hello @/abc<query1> Jarvis" -> "query1"
        '''
        message = message[:index] + message[index+len(command)+1:]
        if query_start == 0 or query_end == -1:
            command = command[2:query_start]
            return message, command, None
        else:
            query = command[query_start+1:query_end]
            command = command[2:query_start]
        return message, command, query
    else:
        return None, None, None

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
        data = request.get_json()
        message = data.get("message")
        # history = request.form.get("history")
        history = []

        # Get command
        command, query = get_command(message)
        context = None
        if command and command in ["search", "weather", "wikipedia", "gmail"]:
            # Search DuckDuckGo and take it as the context
            # only when there is a query
            if command == "search" and query:
                region = "vn-vi" if data.get("region") == "Vietnam" else "uk-en" # Could be Vietnam or International
                search_results = search(search_query = query, place = place, region = region)
                context = "Base on the search result to answer question:\n"
                for s in search_results:
                    context += "* " + s["body"]
                    context += "\n"
            # Look up the weather and put into context
            elif command == "weather":
                place = data.get("place")
                region = "vn-vi" if data.get("region") == "Vietnam" else "uk-en" # Could be Vietnam or International
                
                # Get weather context: query -> place -> else
                if query:
                    weather_info = lookup_weather(place = query, region = region)
                elif place:
                    weather_info = lookup_weather(place = place, region = region)
                else:
                    weather_info = [{"body": "No information on region to retrieve weather information."}]
                context = "Weather news:\n"
                for w in weather_info:
                    context += "* " + w["body"]
                    context += "\n"
            # Search for information about something on Wikipedia
            elif command == "wikipedia":
                language = "vi" if data.get("region") == "Vietnam" else "en"
                context = "Wikipedia information: " + get_wiki_first_paragraph(query, language)
            # Send email
            elif command == "gmail":
                # Get email
                subject = data.get("subject")
                content = data.get("content")
                sender_email = data.get("sender_email")
                receiver_email = data.get("receiver_email")
                password = data.get("password")

                # Send email
                status = send_email(subject, content, sender_email, receiver_email, password)

                return jsonify({
                "message": status,
                "role": "assistant",
                }), 200

        # Models
        message = context + "\n" + message
        answer = respond(message = message, history = history, model = "gemma-3-1b-it-Q8_0.gguf")

        return jsonify({
            "message": answer,
            "role": "assistant",
            }), 200
    return jsonify({"error": "Wrong method! This URL is only for POST method"}), 404

if __name__ == "__main__":
    print(get_command("hello @/abc<query1> Jarvis"))