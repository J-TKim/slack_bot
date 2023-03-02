import os

from dotenv import load_dotenv
from typing import List, Dict, Optional

import openai


load_dotenv()
# API credentials
openai.api_key = os.environ['OPEN_AI_TOKEN']
CHATGPT_ENGINE = os.environ['CHATGPT_ENGINE']

def get_answer(prompt: str, history: Optional[List[Dict[str, str]]] = []) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages= history + [
            {"role": "user", "content": prompt},
        ]
    )

    return response["choices"][0]["message"]["content"]


if __name__ == "__main__":
    history = [
        {"role": "user", "content": "hello?"},
        {"role": "assistant", "content": "Hello! How can I assist you today?"},
        {"role": "user", "content": "how do you think about Hippopotamus"},
        {"role": "assistant",
         "content": "As an AI language model, I do not have personal opinions or emotions like humans do. However, Hippopotamuses are fascinating creatures and one of the largest mammals on Earth. They are known for their massive size, strong jaws, and herbivorous diet. Their unique characteristics and behavior make them an interesting topic to learn about."},
    ]
    prompt = "can you tell me again in korean?"

    print(get_answer(prompt, history))

