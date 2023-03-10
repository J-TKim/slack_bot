import logging
import os
import threading
from typing import Dict, List, Union

from fastapi import APIRouter, Body

from core.slack.slack_api import slackAPI
from core.slack.slack_func import SlackParser
from core.translator.google_translator import translate_text
from models.challenge import Challenge
from core.chatGPT.Official import get_answer

from openai.error import ServiceUnavailableError, APIError, InvalidRequestError


router = APIRouter()


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
    elif cmd == "hello":
        th = threading.Thread(target=hello, args=(channel_id, user_id))
        th.start()
    elif cmd == "jeongtest":
        th = threading.Thread(target=jeongtest, args=(channel_id,))
        th.start()
    elif cmd == "google/to_kr":
        th = threading.Thread(target=google_translator_to_kr, args=(channel_id, thread_ts, text))
        th.start()
    elif cmd == "google/to_en":
        th = threading.Thread(target=google_translator_to_en, args=(channel_id, thread_ts, text))
        th.start()
    elif cmd == "root" or cmd not in api_lists:
        logging.info(cmd)
        channel_id = SlackParser.get_channel_id(request_body)
        thread_ts = SlackParser.get_event_ts(request_body)
        th = threading.Thread(target=temp, args=(channel_id, thread_ts))
        th.start()

    logging.info("---main_end---")
    return {"status": "ok"}


# TODO ????????? ?????? ?????? api ????????? ??????
@router.post("/temp")
def temp(channel_id: str, message_ts: str) -> Dict[str, List[str]]:
    """
    ????????? ?????????, ????????? ????????????.
    :param channel_id: ?????? ?????????
    :param message_ts: ????????? ts
    :return:
    """
    text = "?????? ??????????????? ??????????????????\n" + "\n".join([f"path: {r.path}\t name: {r.name}" for r in router.routes])
    text += "\n" + f"example) <@{os.environ['SLACK_BOT_USER_ID']}> chatGPT ?????? ?????????"
    slackAPI.post_thread_message(channel_id, message_ts, text)

    return {"routes": router.routes}

@router.post("/jeongtest")
def jeongtest() -> Dict[str, str]:
    f"""
    ???????????? ?????????, {os.environ['SLACK_BOT_ADMIN_USER_ID']} ?????? 200??? ??????
    :return: {"status": "ok"}
    """
    user_id = os.environ['SLACK_BOT_ADMIN_USER_ID']

    slackAPI.post_message("C02JD3EMR6X", f"<@{user_id}> 200")

    return {"status": "ok"}

@router.post("/hello")
def hello(channel_id: str, user_id: str) -> Dict[str, str]:
    """
    ??????????????? ?????? ???????????? ???????????? ??????
    :param channel_id: ?????? ?????????
    :param user_id: ????????? ?????? ?????????
    :return: {"status": "ok"}
    """

    slackAPI.post_message(channel_id, f"??????????????? <@{user_id}>!")
    return {"status": "ok"}


@router.post("/chatGPT")
def chatGPT(channel_id: str, thread_ts: str, text: str) -> Dict[str, str]:
    try:
        history = SlackParser.thread_messages_to_openai_history_form(slackAPI.get_all_thread_messages(channel_id, thread_ts))[:-1]
    except Exception as e:
        raise e

    try:
        answer = get_answer(text, history)
    except ServiceUnavailableError or APIError as e:
        answer = "????????? ??????????????????. ?????? ??? ?????? ??????????????????.\n" + str(e)
    except InvalidRequestError as e:
        answer = "InvalidRequestError.\n" + str(e)

    slackAPI.post_thread_message(channel_id, thread_ts, "chatGPT\n" + answer)

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