import os

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

    experience = package.get(
        "description",
        ""
    )

    included_items = []

    if package.get("food"):
        included_items.append("authentic local food")

    if package.get("stay"):
        included_items.append("local-style stay")

    if package.get("camping"):
        included_items.append("camping")

    if package.get("local_experience"):
        included_items.append("local experiences")

    if package.get("transport"):
        included_items.append("transport")

    if package.get("activities"):
        included_items.append("local activities")


    inclusions_text = ", ".join(
        included_items
    )


    # =====================================================
    # AI PROMPT
    # =====================================================

    prompt = f"""
You are the official TravelVibe AI Trip Planner.

TravelVibe creates authentic local travel experiences
across South India.

The philosophy is:

"Explore Local. Set Your Budget. We'll Find Your Vibe."

Create a personalized travel experience based ONLY
on the information provided below.

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
{", ".join(interests) if interests else "General local experience"}

TravelVibe experience available:
{experience}

Included experiences:
{inclusions_text}

IMPORTANT RULES:

1. Do NOT invent prices.
2. Do NOT invent availability.
3. Do NOT invent a confirmed booking.
4. Do NOT mention internal package names or levels.
5. Use the provided budget only.
6. Do not promise anything that was not provided.
7. Present this as a suggested experience, not a confirmed booking.
8. Keep the experience authentic and focused on local culture.
9. If something cannot be confirmed, say that TravelVibe
   will confirm it with the traveller.
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

Day 2:
- Activities
- Local experiences
- Food/culture

Continue for additional days when necessary.

🍛 What You Can Experience

List the relevant experiences.

💰 Your Budget

Explain that the requested experience fits the
traveller's approximate budget.

🤝 What Happens Next

Tell the traveller that TravelVibe will confirm
the final itinerary, availability and exact arrangements.

Finish with:

"Don't just visit. Live the place. 🌴"
"""


    # =====================================================
    # GEMINI REQUEST
    # =====================================================

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )


    return response.text
