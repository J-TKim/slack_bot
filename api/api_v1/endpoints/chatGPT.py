from typing import Any, Dict
from fastapi import APIRouter

from core.chatGPT.Official import get_answer

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
    except Exception as e:
        answer = "알 수 없는 오류가 발생했습니다.\n" + str(e)
        return {"answer": answer, "error": e}

    return {"input": text, "answer": answer}
