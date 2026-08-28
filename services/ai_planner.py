import os
import time

from google import genai


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

    # =====================================================
    # PACKAGE EXPERIENCE
    # =====================================================

    experience = package.get(
        "description",
        ""
    )


    # =====================================================
    # INCLUDED ITEMS
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


    # =====================================================
    # INTERESTS
    # =====================================================

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
    # GEMINI REQUEST
    # =====================================================

    max_attempts = 3


    for attempt in range(max_attempts):

        try:

            print(
                f"TravelVibe Gemini request "
                f"{attempt + 1}/{max_attempts}"
            )


            response = client.models.generate_content(

                model="gemini-3.6-flash",

                contents=prompt

            )


            # =================================================
            # CHECK RESPONSE
            # =================================================

            if response and response.text:

                print(
                    "TravelVibe Gemini response received."
                )

                return response.text


            print(
                "Gemini returned an empty response."
            )


        except Exception as error:

            print(
                f"Gemini error on attempt "
                f"{attempt + 1}: {error}"
            )


            # =================================================
            # RETRY
            # =================================================

            if attempt < max_attempts - 1:

                wait_time = (
                    2 ** attempt
                )

                print(
                    f"Retrying Gemini in "
                    f"{wait_time} seconds..."
                )

                time.sleep(
                    wait_time
                )

                continue


    # =====================================================
    # GEMINI UNAVAILABLE FALLBACK
    # =====================================================

    print(
        "Gemini unavailable after all attempts."
    )


    return f"""
🌴 YOUR TRAVELVIBE

We've received your travel requirements for
{destination}.

📍 Destination

Your trip is planned around {destination},
with a focus on your selected interests
and local TravelVibe experiences.

🗓️ Suggested Experience

Your requested trip is for {days} day(s)
and {travellers} traveller(s).

🍛 What You Can Experience

{inclusions_text or "Local experiences based on your preferences"}

💰 Your Budget

Your requested total budget is
₹{total_budget:,.0f}.

That's approximately
₹{budget_per_person:,.0f} per person.

🤝 What Happens Next

Our AI planner is temporarily busy.

Your requirements have been received.
TravelVibe will confirm the final itinerary,
availability and exact arrangements with you.

Don't just visit. Live the place. 🌴
"""
