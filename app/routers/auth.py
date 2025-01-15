from fastapi import HTTPException, Header
from typing import Optional

TOKEN = "teste_token"

def authenticate(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format. Expected Bearer Auth")

    if authorization != 'Bearer ' + TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization token")

    return
