from dotenv import load_dotenv
import os
from huggingface_hub import hf_hub_download

# Load dotenv
load_dotenv()

# it
gemma_3_1b = "unsloth/gemma-3-1b-it-GGUF"
file_gemma_3_1b = {
    "gemma-3-1b-it-BF16.gguf": "gemma-3-1b-it-BF16.gguf",
    "gemma-3-1b-it-Q8_0.gguf": "gemma-3-1b-it-Q8_0.gguf",
    "gemma-3-1b-it-Q6_K.gguf": "gemma-3-1b-it-Q6_K.gguf",
}

# q4
gemma_3_1b_q4_0 = "google/gemma-3-1b-it-qat-q4_0-gguf"
file_gemma_3_1b_q4_0 = "gemma-3-1b-it-q4_0.gguf"

# Download gguf model files
os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN")  # Replace with your token

if not os.path.exists("./models"):
    os.makedirs("./models")

hf_hub_download(
    repo_id = gemma_3_1b,
    filename = file_gemma_3_1b["gemma-3-1b-it-Q6_K.gguf"],
    local_dir = ".../llm_models", # app/llm_models/
)