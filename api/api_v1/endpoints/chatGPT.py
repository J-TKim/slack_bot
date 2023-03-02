from typing import Any, Dict
from fastapi import APIRouter

import asyncio

from core.chatGPT.Official import get_answer
from core.translator.google_translator import translate_text

from openai.error import ServiceUnavailableError, APIError, InvalidRequestError

router = APIRouter()


@router.get("/health")
def health() -> Any:
    """
    Health check
    """
    return {"status": "ok"}


@router.get("/")
async def chatGPT(text: str) -> Dict[str, str]:
    try:
        answer = get_answer(text)
    except ServiceUnavailableError or APIError as e:
        answer = "서버가 불안정합니다. 잠시 후 다시 시도해주세요.\n" + str(e)
        return {"answer": answer, "error": e}
    except InvalidRequestError as e:
        answer = "InvalidRequestError.\n" + str(e)
        return {"answer": answer, "error": e}

    return {"input": text, "answer": answer}


@router.get("/google/chatGPTkr")
async def chatGPTkr(text: str) -> Dict[str, str]:
    input_en = translate_text(text, "en")
    try:
        answer = get_answer(input_en)
    except ServiceUnavailableError or APIError as e:
        answer = "서버가 불안정합니다. 잠시 후 다시 시도해주세요.\n" + str(e)
        return {"answer": answer, "error": e}
    except InvalidRequestError as e:
        answer = "InvalidRequestError.\n" + str(e)
        return {"answer": answer, "error": e}

    return {"input": text, "input_en": input_en, "answer": answer, "answer_ko": translate_text(answer, "ko")}


@router.get("/google/to_en")
async def google_translator_to_en(text: str) -> Dict[str, str]:
    return {"input": text, "answer": await translate_text(text, "en")}


@router.get("/google/to_kr")
async def google_translator_to_kr(text: str) -> Dict[str, str]:
    return {"input": text, "answer": await translate_text(text, "ko")}

