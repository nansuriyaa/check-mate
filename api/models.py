from sqlalchemy import Column, Integer, String
from api.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, unique=True)
    full_name = Column(String)
    email = Column(String, unique=True)
    hashed_password = Column(String)
