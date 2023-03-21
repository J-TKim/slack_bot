import logging
import os
import threading
from typing import Dict, List, Union

from fastapi import APIRouter, Body

from core.slack.slack_api import slackAPI
from core.slack.slack_func import SlackParser
from core.translator.google_translator import translate_text
from models.challenge import Challenge
from core.openai.chatGPT import (
    get_answer,
    split_messages_under_limit_token
)
from openai.error import ServiceUnavailableError, APIError, InvalidRequestError


router = APIRouter()

logging.basicConfig(level=logging.INFO)


@router.post("/")
async def root(request_body: Union[dict, Challenge] = Body(...)) -> Dict[str, str]:
    logging.info("---main_start---")
    if "challenge" in request_body:
        logging.info("challenge")
        return request_body

    channel_id = SlackParser.get_channel_id(request_body)

    try:
        thread_ts = SlackParser.get_thread_ts(request_body)
    except KeyError:
        thread_ts = SlackParser.get_event_ts(request_body)

    user_id = SlackParser.get_event_user_id(request_body)
    cmd, text = SlackParser.get_cmd_and_text(request_body)
    logging.info(f"channel_id: {channel_id}, thread_ts: {thread_ts}, user_id: {user_id}, cmd: {cmd}, text: {text}")
    api_lists = [r.name for r in router.routes]

    if cmd == "chatGPT":
        th = threading.Thread(target=chatGPT, args=(channel_id, thread_ts, text))
        th.start()
    elif cmd == "pyGPT":
        th = threading.Thread(target=pyGPT, args=(channel_id, thread_ts, text))
        th.start()
    elif cmd == "scalaGPT":
        th = threading.Thread(target=scalaGPT, args=(channel_id, thread_ts, text))
        th.start()
    elif cmd == "hello":
        th = threading.Thread(target=hello, args=(channel_id, user_id))
        th.start()
    elif cmd == "summarize":
        th = threading.Thread(target=summarize, args=(channel_id, thread_ts))
        th.start()
    elif cmd == "root" or cmd not in api_lists:
        logging.info(cmd)
        channel_id = SlackParser.get_channel_id(request_body)
        thread_ts = SlackParser.get_event_ts(request_body)
        th = threading.Thread(target=post_cmd_list, args=(channel_id, thread_ts))
        th.start()

    logging.info("---main_end---")
    return {"status": "ok"}


# TODO 아래에 있는 것들 api 호출로 변경
@router.post("/post_cmd_list")
def post_cmd_list(channel_id: str, message_ts: str) -> Dict[str, List[str]]:
    """
    명령어 리스트, 예시를 알려준다.
    :param channel_id: 채널 아이디
    :param message_ts: 메세지 ts
    :return:
    """
    text = "아래 명령어들을 참고해주세요\n" + "\n".join([f"path: {r.path}\t name: {r.name}" for r in router.routes])
    text += "\n" + f"example) <@{os.environ['SLACK_BOT_USER_ID']}> openai 안녕 정태야"
    slackAPI.post_thread_message(channel_id, message_ts, text)

    return {"routes": router.routes}

@router.post("/hello")
def hello(channel_id: str, user_id: str) -> Dict[str, str]:
    """
    안녕하세요 라고 쓰레드에 보내주는 함수
    :param channel_id: 채널 아이디
    :param user_id: 태그할 유저 아이디
    :return: {"status": "ok"}
    """

    slackAPI.post_message(channel_id, f"안녕하세요 <@{user_id}>!")
    return {"status": "ok"}


@router.post("/chatGPT")
def chatGPT(channel_id: str, thread_ts: str, text: str) -> Dict[str, str]:
    """
    챗지피티가 답변을 쓰레드에 보내주는 함수
    :param channel_id: 채널 아이디
    :param thread_ts: 쓰레드 ts
    :return: {"status": "ok"}
    """
    try:
        history = SlackParser.thread_messages_to_openai_history_form(slackAPI.get_all_thread_messages(channel_id, thread_ts), pattern="chatGPT")[:-1]
    except Exception as e:
        slackAPI.post_thread_message(channel_id, thread_ts, str(e))
        raise e

    try:
        answer = get_answer(text, history)
    except ServiceUnavailableError or APIError as e:
        answer = "서버가 불안정합니다. 잠시 후 다시 시도해주세요.\n" + str(e)
    except InvalidRequestError as e:
        answer = "InvalidRequestError.\n" + str(e)

    slackAPI.post_thread_message(channel_id, thread_ts, "openai\n" + answer)

    logging.info(f"input, {text}, output, {answer}")
    return {"status": "ok"}


@router.post("/pyGPT")
def pyGPT(channel_id: str, thread_ts: str, text: str) -> Dict[str, str]:
    """
    챗지피티가 파이썬 인터프리터 처럼 행동해서 답변을 쓰레드에 보내주는 함수
    :param channel_id: 채널 아이디
    :param thread_ts: 쓰레드 ts
    :return: {"status": "ok"}
    """
    try:
        history = SlackParser.thread_messages_to_openai_history_form(slackAPI.get_all_thread_messages(channel_id, thread_ts), pattern="pyGPT")[:-1]
    except Exception as e:
        slackAPI.post_thread_message(channel_id, thread_ts, str(e))
        raise e

    try:
        system = "I want you to act like a Python interpreter. I will give you Python code, and you will execute it. Do not provide any explanations. Do not respond with anything except the output of the code."
        answer = get_answer(text, history, system)
    except ServiceUnavailableError or APIError as e:
        answer = "서버가 불안정합니다. 잠시 후 다시 시도해주세요.\n" + str(e)
    except InvalidRequestError as e:
        answer = "InvalidRequestError.\n" + str(e)

    slackAPI.post_thread_message(channel_id, thread_ts, "pyGPT\n" + answer)

    logging.info(f"input, {text}, output, {answer}")
    return {"status": "ok"}

@router.post("/scalaGPT")
def scalaGPT(channel_id: str, thread_ts: str, text: str) -> Dict[str, str]:
    """
    챗지피티가 스칼라 인터프리터 처럼 행동해서 답변을 쓰레드에 보내주는 함수
    :param channel_id: 채널 아이디
    :param thread_ts: 쓰레드 ts
    :return: {"status": "ok"}
    """
    try:
        history = SlackParser.thread_messages_to_openai_history_form(slackAPI.get_all_thread_messages(channel_id, thread_ts), pattern="scalaGPT")[:-1]
    except Exception as e:
        slackAPI.post_thread_message(channel_id, thread_ts, str(e))
        raise e

    try:
        system = "I want you to act like a Scala interpreter. I will give you Scala code, and you will execute it. Do not provide any explanations. Do not respond with anything except the output of the code."
        answer = get_answer(text, history, system)
    except ServiceUnavailableError or APIError as e:
        answer = "서버가 불안정합니다. 잠시 후 다시 시도해주세요.\n" + str(e)
    except InvalidRequestError as e:
        answer = "InvalidRequestError.\n" + str(e)

    slackAPI.post_thread_message(channel_id, thread_ts, "scalaGPT\n" + answer)

    logging.info(f"input, {text}, output, {answer}")
    return {"status": "ok"}


@router.post("/google/to_kr")
def google_translator_to_kr(channel_id: str, message_ts: str, text: str) -> Dict[str, str]:
    answer = translate_text(text, "ko")
    slackAPI.post_thread_message(channel_id, message_ts, answer)

    return {"status": "ok"}


@router.post("/google/to_en")
def google_translator_to_en(channel_id: str, message_ts: str, text: str) -> Dict[str, str]:
    answer = translate_text(text, "en")
    slackAPI.post_thread_message(channel_id, message_ts, answer)

    return {"status": "ok"}

@router.post("/summarize")
def summarize(channel_id: str, thread_ts: str) -> Dict[str, str]:
    """
    쓰레드의 내용을 요약해서 쓰레드에 남김.
    :param channel_id: 채널 아이디
    :param thread_ts: 쓰레드 ts
    :return: {"status": "ok"}
    """
    logging.info(f"summarize, {channel_id}, {thread_ts}")
    slack_thread_history = [{"message": message_data['message'], "user_id": f"<@{message_data['user_id']}>"}for message_data in slackAPI.get_all_thread_messages(channel_id, thread_ts)]

    split_slack_thread_history = split_messages_under_limit_token(slack_thread_history, 2**12 - 500)
    middle_prompt = ""
    try:
        if len(split_slack_thread_history) == 1:
            answer = get_answer("아래 대화 내용을 요약해줘\n" + '\n'.join(map(str, split_slack_thread_history[0])))

        else:
            for idx, slack_thread_data in enumerate(split_slack_thread_history):
                logging.info(f"idx: {idx}")
                temp = get_answer("아래 대화 내용을 요약해줘\n" + '\n'.join(map(str, slack_thread_data))) + "\n"
                middle_prompt += temp
            answer = get_answer("아래 대화 내용을 요약해줘\n" + middle_prompt)

    except ServiceUnavailableError or APIError as e:
        logging.info(str(e))
        answer = "서버가 불안정합니다. 잠시 후 다시 시도해주세요.\n" + str(e)
    except InvalidRequestError as e:
        logging.info(str(e))
        answer = "InvalidRequestError.\n" + str(e)

    slackAPI.post_thread_message(channel_id, thread_ts, "summarize\n" + answer)

    return {"status": "ok"}