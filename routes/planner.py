from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional

from database.database import (
    find_travel_package,
    list_planner_destinations
)

from services.ai_planner import (
    generate_travel_plan
)


# =========================================================
# ROUTER
# =========================================================

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

    interests: List[str] = Field(
        default_factory=list
    )


# =========================================================
# GET PLANNER DESTINATIONS
# =========================================================

@router.get("/destinations")
def get_planner_destinations():

    destinations = list_planner_destinations()

    return {
        "success": True,
        "destinations": destinations
    }


# =========================================================
# RECOMMEND TRIP
# =========================================================

@router.post("/recommend")
def recommend_trip(
    request: PlannerRequest
):

    # =====================================================
    # 1. CALCULATE BUDGET PER PERSON
    # =====================================================

    budget_per_person = (
        request.budget /
        request.travellers
    )


    # =====================================================
    # 2. FIND TRAVELVIBE PACKAGE
    # =====================================================

    package = find_travel_package(
        request.destination,
        budget_per_person,
        request.days
    )


    # =====================================================
    # 3. PREPARE TRAVELVIBE DATA
    # =====================================================

    if package:

        budget_match = True

        experience = package.get(
            "description",
            ""
        )

        includes = {

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

        }

    else:

        # No predefined TravelVibe package.
        # The AI can still create a destination-based
        # suggested itinerary.

        budget_match = False

        experience = (
            "No predefined TravelVibe package is currently "
            "available for this destination. The AI will "
            "create a suggested experience based on the "
            "destination, budget, duration and interests."
        )

        includes = {

            "food": False,

            "stay": False,

            "camping": False,

            "local_experience": False,

            "transport": False,

            "activities": False

        }


    # =====================================================
    # 4. GENERATE AI PLAN
    # =====================================================

    try:

        ai_plan = generate_travel_plan(

            destination=request.destination,

            travellers=request.travellers,

            days=request.days,

            total_budget=request.budget,

            budget_per_person=budget_per_person,

            preferred_date=request.preferred_date,

            interests=request.interests,

            package=package

        )

    except Exception as error:

        print(
            "AI PLANNER ERROR:",
            repr(error)
        )

        return {

            "success": False,

            "error": "AI planner failed",

            "details": str(error),

            "destination":
                request.destination,

            "travellers":
                request.travellers,

            "days":
                request.days,

            "total_budget":
                request.budget,

            "budget_per_person":
                round(
                    budget_per_person
                ),

            "preferred_date":
                request.preferred_date,

            "interests":
                request.interests

        }


    # =====================================================
    # 5. RETURN RESULT
    # =====================================================

    return {

        "success": True,

        "budget_match":
            budget_match,

        "destination":
            request.destination,

        "travellers":
            request.travellers,

        "days":
            request.days,

        "total_budget":
            request.budget,

        "budget_per_person":
            round(
                budget_per_person
            ),

        "preferred_date":
            request.preferred_date,

        "interests":
            request.interests,

        "experience":
            experience,

        "includes":
            includes,

        "ai_plan":
            ai_plan,

        "message":
            "Your TravelVibe plan is ready. 🌴"

    }
