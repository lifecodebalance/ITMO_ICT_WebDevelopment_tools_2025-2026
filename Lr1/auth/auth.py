from datetime import datetime, timedelta
import os

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlmodel import Session, select

from connection import get_session
from models import User

load_dotenv()


class AuthService:
    bearer_scheme = HTTPBearer()
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    access_token_lifetime_hours = 8

    def _get_secret_key(self) -> str:
        secret_key = os.getenv("SECRET_KEY")
        if not secret_key:
            raise RuntimeError("SECRET_KEY environment variable is not set")
        return secret_key

    def hash_password(self, plain_password: str) -> str:
        return self.password_context.hash(plain_password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.password_context.verify(plain_password, hashed_password)

    def create_token(self, username: str) -> str:
        issued_at = datetime.utcnow()
        token_payload = {
            "exp": issued_at + timedelta(hours=self.access_token_lifetime_hours),
            "iat": issued_at,
            "sub": username,
        }
        return jwt.encode(token_payload, self._get_secret_key(), algorithm="HS256")

    def decode_token(self, token: str) -> str:
        try:
            payload = jwt.decode(token, self._get_secret_key(), algorithms=["HS256"])
            return payload["sub"]
        except jwt.ExpiredSignatureError as exc:
            raise HTTPException(status_code=401, detail="Expired token") from exc
        except jwt.InvalidTokenError as exc:
            raise HTTPException(status_code=401, detail="Invalid token") from exc

    def get_current_user(
        self,
        auth_credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
        db_session: Session = Depends(get_session),
    ) -> User:
        credentials_error = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        username = self.decode_token(auth_credentials.credentials)
        user_record = db_session.exec(
            select(User).where(User.username == username)
        ).first()

        if not user_record:
            raise credentials_error

        return user_record


auth_service = AuthService()
