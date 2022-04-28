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
    NO_QR_DETECTED = HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                    detail="400 - No QR found in document. Does the document contain a QR code?",
                    headers={"WWW-Authenticate": "Bearer"})
    QR_NOT_FOUND = HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                    detail="400 - No QR found in document. QR unreadable.",
                    headers={"WWW-Authenticate": "Bearer"})
    UNREADABLE_FILE_FITZ = HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                detail="400 - Fitz library can't read PDF document",
                headers={"WWW-Authenticate": "Bearer"})
    FILE_ALREADY_DOWNLOADED = HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                detail="400 - Can't find file, it might have been downloaded already",
                headers={"WWW-Authenticate": "Bearer"})