from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional

from database.database import (
    find_travel_package,
    list_planner_destinations,
    get_travel_itinerary
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
# GET DESTINATIONS
# =========================================================

@router.get("/destinations")
def get_planner_destinations_api():

    destinations = list_planner_destinations()

    return {
        "success": True,
        "destinations": destinations
    }


# =========================================================
# CREATE DATABASE ITINERARY FALLBACK
# =========================================================

def build_database_itinerary(
    destination,
    itinerary
):

    if not itinerary:

        return (
            f"🌴 YOUR TRAVELVIBE\n\n"
            f"We received your request for {destination}.\n\n"
            "We are preparing a personalized experience "
            "for your destination, budget and travel style.\n\n"
            "TravelVibe will confirm the final itinerary, "
            "availability and arrangements with you.\n\n"
            "Don't just visit. Live the place. 🌴"
        )


    lines = []

    lines.append(
        "🌴 YOUR TRAVELVIBE"
    )

    lines.append("")

    lines.append(
        f"Here's a suggested {destination} "
        "experience built around your requirements."
    )

    lines.append("")

    lines.append(
        "🗓️ Suggested Experience"
    )

    lines.append("")


    # =====================================================
    # BUILD EACH DAY
    # =====================================================

    for day in itinerary:

        day_number = day.get(
            "day_number",
            ""
        )

        lines.append(
            f"Day {day_number}:"
        )


        morning = day.get(
            "morning"
        )

        afternoon = day.get(
            "afternoon"
        )

        evening = day.get(
            "evening"
        )

        food = day.get(
            "food"
        )

        local_experience = day.get(
            "local_experience"
        )


        if morning:

            lines.append(
                f"- Morning: {morning}"
            )


        if afternoon:

            lines.append(
                f"- Afternoon: {afternoon}"
            )


        if evening:

            lines.append(
                f"- Evening: {evening}"
            )


        if food:

            lines.append(
                f"- Food: {food}"
            )


        if local_experience:

            lines.append(
                f"- Local experience: "
                f"{local_experience}"
            )


        lines.append("")


    lines.append(
        "🍛 What You Can Experience"
    )

    lines.append("")


    # =====================================================
    # COLLECT UNIQUE FOOD / LOCAL EXPERIENCES
    # =====================================================

    food_items = []
    local_items = []


    for day in itinerary:

        food = day.get(
            "food"
        )

        local_experience = day.get(
            "local_experience"
        )


        if food and food not in food_items:

            food_items.append(
                food
            )


        if (
            local_experience
            and
            local_experience not in local_items
        ):

            local_items.append(
                local_experience
            )


    for item in food_items:

        lines.append(
            f"- {item}"
        )


    for item in local_items:

        lines.append(
            f"- {item}"
        )


    lines.append("")

    lines.append(
        "🤝 What Happens Next"
    )

    lines.append("")

    lines.append(
        "TravelVibe will confirm the final itinerary, "
        "availability, exact pricing and arrangements "
        "with you."
    )

    lines.append("")

    lines.append(
        "Don't just visit. Live the place. 🌴"
    )


    return "\n".join(lines)


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

    except Exception as error:

        print(
            "PACKAGE SEARCH ERROR:",
            repr(error)
        )

        package = None


    # =====================================================
    # 3. GET DATABASE ITINERARY
    # =====================================================

    try:

        itinerary = get_travel_itinerary(
            request.destination,
            budget_per_person,
            request.days
        )

    except Exception as error:

        print(
            "ITINERARY SEARCH ERROR:",
            repr(error)
        )

        itinerary = []


    # =====================================================
    # 4. PREPARE PACKAGE INFORMATION
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
            "A personalized TravelVibe experience "
            "based on the selected destination, "
            "budget, duration and interests."
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
    # 5. CREATE DATABASE FALLBACK FIRST
    # =====================================================

    database_plan = build_database_itinerary(
        request.destination,
        itinerary
    )


    # =====================================================
    # 6. TRY GEMINI
    # =====================================================

    ai_plan = None

    ai_available = False


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

        if ai_plan:

            ai_available = True


    except Exception as error:

        print(
            "AI PLANNER ERROR:",
            repr(error)
        )

        ai_plan = None

        ai_available = False


    # =====================================================
    # 7. CHOOSE FINAL PLAN
    # =====================================================

    final_plan = (

        ai_plan

        if ai_available

        else database_plan

    )


    # =====================================================
    # 8. RETURN RESULT
    # =====================================================

    return {

        "success": True,

        "budget_match":
            budget_match,

        "ai_available":
            ai_available,

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

        "itinerary":
            itinerary,

        "ai_plan":
            final_plan,

        "message":
            "Your TravelVibe plan is ready. 🌴"

    }
