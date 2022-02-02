from pydantic import BaseModel,Field
import uuid

class Water(BaseModel):
    ph: float
    hardness: float
    solids: float
    chloramines: float
    sulfate: float
    conductivity: float
    organic_carbon: float
    trihalomethanes: float
    turbidity: float
    job_id:str = Field(default_factory=lambda:uuid.uuid4().hex)