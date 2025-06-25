from pydantic import BaseModel
from typing import List, Literal, Union

class PatchOperation(BaseModel):
    op: Literal["replace"]
    path: str
    value: Union[str, int, float]

PatchRequest = List[PatchOperation]