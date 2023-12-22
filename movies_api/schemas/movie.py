
from pydantic import BaseModel, Field
from typing import Optional,List
from datetime import datetime

class Movie(BaseModel):
    id: Optional[int] = None
    title: str = Field(min_length=5, max_length=15)
    overview: str = Field(min_length=15, max_length=50)
    year: int = Field(le=datetime.now().year)
    rating: float = Field(ge=1,le=10)
    category: str = Field(min_length=5, max_length=15)
    
    model_config = {
     "json_schema_extra": {
            "examples": [
                {
                "id":1,
                "title":"My movie",
                "overview": "My overview For the movie",
                "year":datetime.now().year,
                "rating":10.0,
                "category":"None none"
                }
            ]
        }
    }
