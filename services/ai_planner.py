from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional

from database.database import (
    find_travel_package
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

    interests: List[str] = []


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

    try:

        package = find_travel_package(

            request.destination,

            budget_per_person,

            request.days

        )

    except Exception as e:

        print(
            "SUPABASE PACKAGE SEARCH ERROR:",
            repr(e)
        )

        package = None


    # =====================================================
    # 3. PREPARE PACKAGE INFORMATION
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

        budget_match = False

        experience = (
            "AI-generated local travel experience "
            "based on the destination, budget, "
            "travel dates and interests."
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

            destination=
                request.destination,

            travellers=
                request.travellers,

            days=
                request.days,

            total_budget=
                request.budget,

            budget_per_person=
                budget_per_person,

            preferred_date=
                request.preferred_date,

            interests=
                request.interests,

            package=
                package

        )

    except Exception as e:

        # -------------------------------------------------
        # PRINT ACTUAL ERROR TO RENDER LOGS
        # -------------------------------------------------

        print(
            "AI PLANNER ERROR:",
            repr(e)
        )

        return {

            "success": False,

            "error":
                "AI planner failed",

            "details":
                str(e),

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
    # 5. SUCCESS RESPONSE
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
