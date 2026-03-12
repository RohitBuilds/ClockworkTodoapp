from pydantic import BaseModel,Field
from typing import Union
from sqlalchemy import  Column, ForeignKey, Integer, String, Boolean,DateTime
from database import Base
from datetime import datetime
from sqlalchemy.orm import relationship

class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True,index=True)
    title = Column(String,index=True)
    description = Column(String,index=True)
    completed = Column(Boolean,default=False)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    due_time = Column(DateTime, nullable=True) 
    user = relationship("User", back_populates="todos")