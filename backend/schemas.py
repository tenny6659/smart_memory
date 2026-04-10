from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class EventPromptRequest(BaseModel):
    userId: str
    promptText: str
    timestamp: Optional[datetime] = None

class MemoryBase(BaseModel):
    user_id: str
    text: str
    category: str
    timestamp: datetime
    source: str
    importance_score: float

class MemorySchema(MemoryBase):
    id: int
    class Config:
        from_attributes = True

class DecisionLogSchema(BaseModel):
    prompt: str
    decision: str
    class Config:
        from_attributes = True

class NeighborSchema(BaseModel):
    id: int
    text: str
    relation: str

class MemoryNeighborsResponse(BaseModel):
    memoryId: int
    text: str
    neighbors: List[NeighborSchema]

class ChatResponse(BaseModel):
    response: str
    decision: str
    memory_id: Optional[int] = None
