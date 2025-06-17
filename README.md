# About
A back-end server for a first-year IoT project in Vietnamese German University.

# How to run project:
- Get into root folder of project (the directory including run.py and app/).
- To initialize:
```
docker-compose up --build
```
- After that, each time you run project, use this command:
```
docker-compose up
```

# Routes
## Authentication

## **Chatbot route**: For more information on input format, see file ./app/routes/chatbot
- chatbot/vanilla for casual chatting with Gemma 3 1B
- chatbot/function_call_chatbot for chatting with Gemma 3 1B equipped with function calling ability:
    + func_list = [search_func, weather_func, wikipedia_func]
    + Search function: using DuckDuckGo Search Engine.
    + Weather function: search function but for weather.
    + Wikipedia function: a function to retrieve the first paragraph of Wikipedia using the website's API. If there is an error in the process (due to different formatting, which is quite common), then the short information about it will be returned (the one interactively appearing when searching in Wikipedia's search).
    + Gmail function: still in development, error due to JSON parsing of LLM's respond (could be because of endline).
- chatbot/bluetooth_processor for command processing chatbot utilizing Llama 3.2 1B finetuned on custom dataset.