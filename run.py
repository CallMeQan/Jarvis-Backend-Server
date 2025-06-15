import os

MODEL_DIR = os.path.join(os.path.dirname(__file__), 'app', 'llm_models')
MODEL_LIST = [
    "gemma-3-1b-it-Q8_0.gguf",
    "Llama-3.2-1B-Instruct-GRPO-GGUF.gguf",
    "Llama-3.2-1B-Instruct-Q8_0.gguf"
]

if __name__ == "__main__":
    import app
    pp = app.create_app_with_blueprint()
    pp.run(debug=True, host="0.0.0.0")