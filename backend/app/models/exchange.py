from sqlalchemy import Column, Integer, String, Float
from ..database import Base

class Exchange(Base):
    __tablename__ = "exchanges"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    api_url = Column(String)
    trust_score = Column(Float, default=0.5)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Exchange {self.name}>"