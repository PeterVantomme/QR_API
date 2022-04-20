from enum import Enum
from fastapi import HTTPException, status


class Error(Enum):
    ENCODE_ERROR = HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                    detail="400 - Incorrect body, did u encode the PDF-document to base64?",
                    headers={"WWW-Authenticate": "Bearer"})
    INVALID_TOKEN =  HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="401 - Could not validate credentials - Invalid token",
                    headers={"WWW-Authenticate": "Bearer"})
    INVALID_CREDENTIALS = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="401 - Incorrect username or password, make sure to log in and use token in request url.",
                    headers={"WWW-Authenticate": "Bearer"})
    UNREADABLE_FILE = HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                    detail="400 - Can't read PDF document",
                    headers={"WWW-Authenticate": "Bearer"})
    INVALID_FILE = HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                    detail="400 - Can't find document, did u add it in the request?",
                    headers={"WWW-Authenticate": "Bearer"})