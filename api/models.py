from sqlalchemy import Column, Integer, String
from api.database import Base 


class Screenshot(Base):
    __tablename__ ='screenshots',
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    url = Column(String(255), unique=True, nullable=False)
    s3_path = Column(String(255), nullable=False)
