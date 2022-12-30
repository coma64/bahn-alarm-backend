from fastapi import HTTPException, status
from pydantic import BaseModel


class HttpErrorModel(BaseModel):
    detail: str


NOT_FOUND = {
    status.HTTP_404_NOT_FOUND: {"model": HttpErrorModel},
}
NOT_FOUND_EXCEPTION = HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
