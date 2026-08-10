from sqlalchemy import Column, Integer, String
from backend.database.db import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    category = Column(String)
    trend_score = Column(Integer)
    stage = Column(String)