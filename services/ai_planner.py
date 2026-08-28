import os
import time

from google import genai
from google.genai import errors


# =========================================================
# GEMINI CLIENT
# =========================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY environment variable is missing"
    )


client = genai.Client(
    api_key=GEMINI_API_KEY
)


# =========================================================
# TRAVELVIBE AI PLANNER
# =========================================================

def generate_travel_plan(
    destination,
    travellers,
    days,
    total_budget,
    budget_per_person,
    preferred_date,
    interests,
    package
):

    experience = package.get(
        "description",
        ""
    )


    # =====================================================
    # BUILD INCLUDED EXPERIENCES
    # =====================================================

    included_items = []


    if package.get("food"):
        included_items.append(
            "authentic local food"
        )


    if package.get("stay"):
        included_items.append(
            "local-style stay"
        )


    if package.get("camping"):
        included_items.append(
            "camping"
        )


    if package.get("local_experience"):
        included_items.append(
            "local experiences"
        )


    if package.get("transport"):
        included_items.append(
            "transport"
        )


    if package.get("activities"):
        included_items.append(
            "local activities"
        )


    inclusions_text = ", ".join(
        included_items
    )


    interests_text = (
        ", ".join(interests)
        if interests
        else "General local experience"
    )


    # =====================================================
    # AI PROMPT
    # =====================================================

    prompt = f"""
You are the official TravelVibe AI Trip Planner.

TravelVibe creates authentic local travel experiences
across South India.

TravelVibe philosophy:

"Explore Local. Set Your Budget. We'll Find Your Vibe."

Create a personalized suggested travel experience
based ONLY on the information provided below.

TRAVELLER DETAILS

Destination:
{destination}

Number of travellers:
{travellers}

Number of days:
{days}

Total budget:
₹{total_budget}

Budget per person:
₹{budget_per_person}

Preferred date:
{preferred_date or "Flexible"}

Interests:
{interests_text}

TRAVELVIBE EXPERIENCE AVAILABLE:

{experience}

INCLUDED EXPERIENCES:

{inclusions_text}

IMPORTANT RULES:

1. Do NOT invent prices.
2. Do NOT invent availability.
3. Do NOT invent a confirmed booking.
4. Do NOT mention internal package names or levels.
5. Use the provided budget only.
6. Do not promise anything that was not provided.
7. Present this as a suggested experience.
8. Keep the experience authentic and focused on local culture.
9. If something cannot be confirmed, say TravelVibe will
   confirm it with the traveller.
10. Do not make unrealistic claims.

Create the response in this format:

🌴 YOUR TRAVELVIBE

A short welcoming sentence.

📍 Destination

Brief description of the destination experience.

🗓️ Suggested Experience

Day 1:
- Activities
- Local experiences
- Food/culture

Continue for all requested days.

🍛 What You Can Experience

List the relevant included experiences.

💰 Your Budget

Explain that the suggested experience is designed
around the traveller's provided budget.

🤝 What Happens Next

Tell the traveller that TravelVibe will confirm
the final itinerary, availability and exact arrangements.

Finish with:

"Don't just visit. Live the place. 🌴"
"""


    # =====================================================
    # GEMINI REQUEST WITH RETRIES
    # =====================================================

    max_attempts = 3

    for attempt in range(max_attempts):

        try:

            response = client.models.generate_content(

                model="gemini-3.6-flash",

                contents=prompt

            )


            if response and response.text:

                return response.text


            return (
                "🌴 YOUR TRAVELVIBE\n\n"
                "We have created your TravelVibe "
                "experience based on your destination, "
                "budget and interests.\n\n"
                "TravelVibe will contact you to confirm "
                "the detailed itinerary and arrangements.\n\n"
                "Don't just visit. Live the place. 🌴"
            )


        except errors.ServerError as error:

            # -------------------------------------------------
            # Gemini temporary server problem
            # -------------------------------------------------

            print(
                f"Gemini server error "
                f"(attempt {attempt + 1}/{max_attempts}): "
                f"{error}"
            )


            if attempt < max_attempts - 1:

                # Wait before retrying.
                time.sleep(
                    2 ** attempt
                )

                continue


            # -------------------------------------------------
            # All retries failed
            # -------------------------------------------------

            return (
                "🌴 YOUR TRAVELVIBE\n\n"
                f"We've received your requirements for "
                f"{destination}.\n\n"
                f"Your trip is for {travellers} traveller(s) "
                f"for {days} day(s), with a total budget of "
                f"₹{total_budget:,.0f}.\n\n"
                "Our AI planner is temporarily busy. "
                "TravelVibe will confirm your personalized "
                "itinerary and arrangements with you.\n\n"
                "Don't just visit. Live the place. 🌴"
            )


        except Exception as error:

            # -------------------------------------------------
            # Unexpected Gemini error
            # -------------------------------------------------

            print(
                f"Gemini unexpected error: {error}"
            )


            return (
                "🌴 YOUR TRAVELVIBE\n\n"
                f"We've received your requirements for "
                f"{destination}.\n\n"
                "Your TravelVibe experience is being "
                "prepared. Our team will confirm the "
                "final itinerary and arrangements with you.\n\n"
                "Don't just visit. Live the place. 🌴"
            )
