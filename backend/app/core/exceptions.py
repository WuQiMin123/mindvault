from fastapi import status


class MindVaultError(Exception):
    code: str = "INTERNAL_ERROR"
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message: str = "", details: dict | None = None) -> None:
        self.message = message or self.__class__.__name__
        self.details = details

    def to_dict(self) -> dict:
        return {"error": {"code": self.code, "message": self.message, "details": self.details}}


class NotFoundError(MindVaultError):
    code = "NOT_FOUND"
    status_code = status.HTTP_404_NOT_FOUND


class ValidationError(MindVaultError):
    code = "VALIDATION_ERROR"
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class CrawlerError(MindVaultError):
    code = "CRAWLER_ERROR"
    status_code = status.HTTP_502_BAD_GATEWAY


class LLMError(MindVaultError):
    code = "LLM_ERROR"
    status_code = status.HTTP_502_BAD_GATEWAY
