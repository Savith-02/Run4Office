from pydantic import BaseModel, Field
from typing import Optional

class PositionDataTemplate(BaseModel):
    Position_title: str = Field(..., title="Title of the position")
    Description: Optional[str] = Field(None, title="Description of the position")
    Next_election_date: Optional[str] = Field(None, title="Date of the next election")
    Filing_window_start: Optional[str] = Field(None, title="Start date of filing window")
    Filing_window_end: Optional[str] = Field(None, title="End date of filing window")
    Name_of_district: Optional[str] = Field(None, title="Name of the district")
    State_of_district: Optional[str] = Field(None, title="State of the district")
    Other_relevant_info: Optional[str] = Field(None, title="Any other relevant information")

    class Config:
        schema_extra = {
            "example": {
                "Position_title": "Mayor of Fort Wayne",
                "Description": "Chief executive responsible for proposing budget, signing legislation, appointing directors, and overseeing city operations.",
                "Next_election_date": "2027",
                "Filing_window_start": "February 3, 2023",
                "Filing_window_end": "July 15, 2023",
                "Name_of_district": "N/A",
                "State_of_district": "Indiana",
                "Other_relevant_info": "Current Mayor: Sharon Tucker (D), assumed office April 23, 2024."
            }
        }