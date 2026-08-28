from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional

from database.database import find_travel_package


router = APIRouter(
    prefix="/planner",
    tags=["TravelVibe AI Planner"]
)


# =========================================================
# REQUEST MODEL
# =========================================================

class PlannerRequest(BaseModel):

    destination: str = Field(
        ...,
        min_length=2,
        max_length=150
    )

    travellers: int = Field(
        ...,
        ge=1,
        le=100
    )

    days: int = Field(
        ...,
        ge=1,
        le=30
    )

    budget: float = Field(
        ...,
        gt=0
    )

    preferred_date: Optional[str] = None

    interests: List[str] = []


# =========================================================
# TRAVELVIBE PLANNER
# =========================================================

@router.post("/recommend")
def recommend_trip(request: PlannerRequest):

    # -----------------------------------------------------
    # Calculate budget per person
    # -----------------------------------------------------

    budget_per_person = (
        request.budget / request.travellers
    )


    # -----------------------------------------------------
    # Find matching package from Supabase
    # -----------------------------------------------------

    package = find_travel_package(
        request.destination,
        budget_per_person,
        request.days
    )


    # -----------------------------------------------------
    # No suitable package found
    # -----------------------------------------------------

    if not package:

        return {

            "success": False,

            "destination": request.destination,

            "travellers": request.travellers,

            "days": request.days,

            "total_budget": request.budget,

            "budget_per_person": round(
                budget_per_person
            ),

            "preferred_date": request.preferred_date,

            "interests": request.interests,

            "message":
                "Your current budget may not be enough "
                "for the experience you're looking for. "
                "We can suggest a suitable budget or "
                "alternative experience."
        }


    # -----------------------------------------------------
    # Suitable package found
    # -----------------------------------------------------

    return {

        "success": True,

        "destination": request.destination,

        "travellers": request.travellers,

        "days": request.days,

        "total_budget": request.budget,

        "budget_per_person": round(
            budget_per_person
        ),

        "preferred_date": request.preferred_date,

        "interests": request.interests,

        "experience": package.get(
            "description"
        ),

        "includes": {

            "food": package.get(
                "food",
                False
            ),

            "stay": package.get(
                "stay",
                False
            ),

            "camping": package.get(
                "camping",
                False
            ),

            "local_experience": package.get(
                "local_experience",
                False
            ),

            "transport": package.get(
                "transport",
                False
            ),

            "activities": package.get(
                "activities",
                False
            )

        },

        "message":
            "Yes! We can create a TravelVibe "
            "experience around your requirements."
    }
