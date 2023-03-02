import os
import re
from dotenv import load_dotenv
from typing import List, Dict

import logging

load_dotenv()
SLACK_API_TOKEN = os.environ["SLACK_API_TOKEN"]


class SlackParser:
    @staticmethod
    def get_token(request_body: dict) -> str:
        return request_body["token"]

    @staticmethod
    def get_type(request_body: dict) -> str:
        return request_body["type"]

    @staticmethod
    def get_event_id(request_body: dict) -> str:
        return request_body["event_id"]

    @staticmethod
    def get_channel_id(request_body: dict) -> str:
        return request_body["event"]["channel"]

    @staticmethod
    def get_event_ts(request_body: dict) -> str:
        return request_body["event"]["event_ts"]

    @staticmethod
    def get_text(request_body: dict) -> str:
        return request_body["event"]["text"]

    @staticmethod
    def get_event_type(request_body: dict) -> str:
        return request_body["event"]["type"]

    @staticmethod
    def get_event_user_id(request_body: dict) -> str:
        return request_body["event"]["user"]

    @staticmethod
    def get_cmd_and_text(request_body: dict) -> tuple:
        line = request_body["event"]["text"].split(" ")
        logging.info(line)

        if len(line) < 2:
            return None, None
        elif len(line) >= 3:
            cmd, text = line[1], ' '.join(line[2:])
            return cmd, text
        return line[1], None

    @staticmethod
    def thread_messages_to_openai_history_form(thread_messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        history_list: List[Dict[str, str]] = list()
        SLACK_BOT_USER_ID = os.environ['SLACK_BOT_USER_ID']
        input_pattern = fr"^{re.escape(f'<@{SLACK_BOT_USER_ID}>')}\schatGPT.*$"
        answer_pattern = r"^chatGPT\n.*$"

        for thread_message in thread_messages:
            if thread_message["user_id"] != os.environ['SLACK_BOT_USER_ID']:
                if bool(re.match(input_pattern, thread_message['message'])):
                    history_list.append({"role": "user", "content": thread_message['message']})
            if thread_message['user_id'] == os.environ['SLACK_BOT_USER_ID']:
                if bool(re.match(answer_pattern, thread_message['message'])):
                    history_list.append({"role": "assistant", "content": thread_message['message']})

        return history_list
