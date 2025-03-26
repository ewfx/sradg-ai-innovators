# api/models.py
from pydantic import BaseModel

class RealtimeData(BaseModel):
    TRADEID: int
    RISKDATE: str
    DESKNAME: str
    QUANTITYDIFFERENCE: float
    IMPACT_PRICE: float
    IMPACT_QUANTITY: float
    COMMENT: str

