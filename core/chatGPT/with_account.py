import os
import sys
from dotenv import load_dotenv

from revChatGPT.V2 import Chatbot


load_dotenv()

async def main(inp: str) -> str:
    print("input: ", inp)
    chatbot = Chatbot(email=os.environ['CHATGPT_ID'], password=os.environ['CHATGPT_PW'], paid=True)
    answer = ""
    async for line in chatbot.ask(inp):
        answer += line["choices"][0]["text"].replace("<|im_end|>", "")
        print(answer)
        sys.stdout.flush()
    return answer

if __name__ == "__main__":
    import asyncio
    text = "hello my name is jeongtae"
    print(asyncio.run(main(text)))
