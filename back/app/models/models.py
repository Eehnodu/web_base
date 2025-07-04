"""
models.py
----------

이 파일은 SQLAlchemy의 ORM(Object-Relational Mapping)을 활용해
데이터베이스 테이블 구조를 정의하는 파일입니다.

모든 테이블 모델 클래스는 공통적으로 Base 클래스를 상속받습니다.
Base는 app/database.py 에서 선언되며, 이는 SQLAlchemy의 declarative_base()를 기반으로 합니다.

Base를 상속받는 모든 클래스는 실제 DB 테이블로 매핑되며,
Alembic 등의 마이그레이션 도구에서도 자동으로 인식됩니다.

"""

from app.database import Base
from sqlalchemy import Column, Integer, String, DateTime
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
