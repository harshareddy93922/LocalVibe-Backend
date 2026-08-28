from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional


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
# AI PLANNER
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
    # Temporary package classification
    #
    # IMPORTANT:
    # These are temporary example rules.
    # Later we will move them into Supabase.
    # -----------------------------------------------------

    if budget_per_person < 2500:

        package_type = "basic"

    elif budget_per_person < 4000:

        package_type = "standard"

    elif budget_per_person < 6000:

        package_type = "comfort"

    else:

        package_type = "premium"


    # -----------------------------------------------------
    # Prepare customer-facing response
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

        # Internal information for now.
        # We will NOT send this to customers
        # in the final version.
        "internal_package": package_type,

        "message":
            "TravelVibe has received your trip "
            "requirements and is preparing your "
            "personalised experience."
    }
