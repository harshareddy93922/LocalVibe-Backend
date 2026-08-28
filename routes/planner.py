from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional

from database.database import (
    find_travel_package,
    find_next_travel_package
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
    # 2. FIND EXACT PACKAGE
    # =====================================================

    package = find_travel_package(

        request.destination,

        budget_per_person,

        request.days

    )


    # =====================================================
    # 3. IF NO EXACT PACKAGE
    # =====================================================

    if not package:

        # -------------------------------------------------
        # Look for next suitable package
        # -------------------------------------------------

        next_package = find_next_travel_package(

            request.destination,

            budget_per_person,

            request.days

        )


        # -------------------------------------------------
        # A suitable higher-budget package exists
        # -------------------------------------------------

        if next_package:

            recommended_budget_per_person = float(
                next_package.get(
                    "min_budget_per_person",
                    0
                )
            )


            recommended_total_budget = (
                recommended_budget_per_person
                * request.travellers
            )


            return {

                "success": False,

                "budget_match": False,

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

                "recommended_budget":
                    round(
                        recommended_total_budget
                    ),

                "recommended_budget_per_person":
                    round(
                        recommended_budget_per_person
                    ),

                "preferred_date":
                    request.preferred_date,

                "interests":
                    request.interests,

                "experience":
                    next_package.get(
                        "description",
                        ""
                    ),

                "message":
                    "You're close! 🌿 "
                    "Your current budget may not "
                    "cover the full TravelVibe "
                    "experience you're looking for. "
                    "Based on your requirements, "
                    "we recommend approximately "
                    f"₹{recommended_total_budget:,.0f} "
                    "for this experience."

            }


        # -------------------------------------------------
        # No package at all
        # -------------------------------------------------

        return {

            "success": False,

            "budget_match": False,

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

            "message":
                "We couldn't find a suitable "
                "TravelVibe package for these "
                "requirements yet. "
                "Please contact us and we'll "
                "explore a custom experience "
                "for you."

        }


    # =====================================================
    # 4. GENERATE AI PLAN
    # =====================================================

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


    # =====================================================
    # 5. PREPARE INCLUDED EXPERIENCES
    # =====================================================

    includes = {

        "food":
            package.get(
                "food",
                False
            ),

        "stay":
            package.get(
                "stay",
                False
            ),

        "camping":
            package.get(
                "camping",
                False
            ),

        "local_experience":
            package.get(
                "local_experience",
                False
            ),

        "transport":
            package.get(
                "transport",
                False
            ),

        "activities":
            package.get(
                "activities",
                False
            )

    }


    # =====================================================
    # 6. SUCCESS RESPONSE
    # =====================================================

    return {

        "success": True,

        "budget_match": True,

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
            package.get(
                "description",
                ""
            ),

        "includes":
            includes,

        "ai_plan":
            ai_plan,

        "message":
            "Your TravelVibe plan is ready. 🌴"

    }
