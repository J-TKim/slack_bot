import os
from dotenv import load_dotenv
from typing import List, Dict, Optional

import openai
import tiktoken


load_dotenv()
# API credentials
openai.api_key = os.environ['OPEN_AI_TOKEN']
CHATGPT_ENGINE = os.environ['CHATGPT_ENGINE']

def get_answer(prompt: str, history: Optional[List[Dict[str, str]]]= [], system: Optional[str] = None) -> str:

    if system:
        history += [{"role": "system", "content": system}]
    response = openai.ChatCompletion.create(
        model = CHATGPT_ENGINE,
        messages = \
            history + \
            [{"role": "user", "content": prompt},]
    )

    print([{"role": "system", "content": system}] if system else [] + \
            history + \
            [{"role": "user", "content": prompt},])

    return response["choices"][0]["message"]["content"]

def num_tokens_from_messages(messages):
  """Returns the number of tokens used by a list of messages."""
  try:
      encoding = tiktoken.encoding_for_model(CHATGPT_ENGINE)
  except KeyError:
      encoding = tiktoken.get_encoding("cl100k_base")
  if CHATGPT_ENGINE == CHATGPT_ENGINE:  # note: future models may deviate from this
      num_tokens = 0
      for message in messages:
          num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
          for key, value in message.items():
              num_tokens += len(encoding.encode(value))
              if key == "name":  # if there's a name, the role is omitted
                  num_tokens += -1  # role is always required and always 1 token
      num_tokens += 2  # every reply is primed with <im_start>assistant
      return num_tokens
  else:
      raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
  See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")

def split_messages_under_limit_token(messages: List[Dict[str, str]], limit:int =2**12) -> List[List[Dict[str, str]]]:
    if num_tokens_from_messages(messages) <= limit:
        return [messages]
    else:
        messages_len = len(messages)
        return split_messages_under_limit_token(messages=messages[:messages_len//2], limit=limit) + split_messages_under_limit_token(messages[messages_len//2:], limit=limit)


if __name__ == "__main__":
    system = "I want you to act like a Python interpreter. I will give you Python code, and you will execute it. Do not provide any explanations. Do not respond with anything except the output of the code."
    history = []
    prompt = "print(100)"

    print(get_answer(prompt, history, system))

    print(split_messages_under_limit_token(history))
