import os

from google import genai
from google.genai import types


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
    package=None
):

    # =====================================================
    # SAFELY HANDLE MISSING PACKAGE
    # =====================================================

    package = package or {}

    experience = package.get(
        "description",
        "No specific TravelVibe package is currently available."
    )

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

    inclusions_text = (
        ", ".join(included_items)
        if included_items
        else "No predefined TravelVibe package"
    )


    # =====================================================
    # AI PROMPT
    # =====================================================

    prompt = f"""
You are the official TravelVibe AI Trip Planner.

TravelVibe is a budget-first travel planning platform
focused on authentic local experiences in India.

The philosophy is:

"Explore Local. Set Your Budget. We'll Find Your Vibe."


=========================================================
YOUR ROLE
=========================================================

Create a useful, realistic and personalized travel
suggestion based on the traveller's destination,
number of travellers, number of days, budget,
preferred date and interests.

A destination does NOT need to exist in the TravelVibe
database.

If there is no predefined TravelVibe package, still
create a useful suggested itinerary using reliable
destination information obtained through Google Search.


=========================================================
GOOGLE SEARCH
=========================================================

You have access to Google Search.

Use Google Search when appropriate to research:

- destination information
- attractions
- local culture
- local food
- things to do
- nature experiences
- villages
- historical places
- travel conditions
- publicly available destination information
- current information that may have changed

Do not invent destination facts.

Prefer reliable and current information.


=========================================================
TRAVELLER DETAILS
=========================================================

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


=========================================================
TRAVELVIBE INFORMATION
=========================================================

TravelVibe experience:

{experience}

TravelVibe included services:

{inclusions_text}


=========================================================
IMPORTANT RULES
=========================================================

1. The customer's budget is the PRIMARY constraint.

2. Prefer affordable experiences.

3. Prefer authentic local experiences over generic
   tourist recommendations when appropriate.

4. Consider the traveller's interests carefully.

5. Use Google Search for destination facts when necessary.

6. Do NOT invent destination facts.

7. Do NOT invent exact hotel availability.

8. Do NOT invent booking confirmations.

9. Do NOT claim TravelVibe has a local partner unless
   that information is explicitly provided.

10. Do NOT invent exact prices.

11. If publicly listed prices are found through Google
    Search, describe them as approximate or publicly
    listed prices.

12. Do NOT guarantee that the complete trip fits the
    requested budget unless the available information
    supports that conclusion.

13. If the requested budget appears tight, prioritize
    lower-cost activities and explain that final pricing
    must be confirmed.

14. If the destination has no TravelVibe package, still
    create a useful suggested itinerary.

15. Do NOT expose internal database information.

16. Do NOT expose internal package names.

17. Do NOT claim an experience is confirmed.

18. Clearly tell the traveller that TravelVibe will
    confirm final prices, availability and arrangements.

19. The itinerary is a SUGGESTION, not a booking.

20. Do not stop simply because a TravelVibe package
    does not exist.


=========================================================
CREATE THE RESPONSE
=========================================================

Create a personalized TravelVibe itinerary.


🌴 YOUR TRAVELVIBE

Write a short welcoming sentence.


📍 Destination

Give a useful description of the destination based on
reliable information.


🗓️ Suggested Experience

Day 1:
- Places to explore
- Local experiences
- Food/culture

Day 2:
- Places to explore
- Local experiences
- Food/culture

Continue for the remaining days.


🍛 What You Can Experience

List the most relevant experiences based on the
traveller's interests.


💰 Your Budget

Explain how the suggested experience relates to the
traveller's requested budget.

Do not invent a detailed cost breakdown unless reliable
public pricing information is available.


🌿 Why This Fits Your Vibe

Explain how the itinerary matches the traveller's
interests.


🤝 What Happens Next

Tell the traveller that TravelVibe will confirm the
final itinerary, availability, exact prices and
arrangements.


Finish with exactly:

"Don't just visit. Live the place. 🌴"
"""


    # =====================================================
    # GOOGLE SEARCH GROUNDING
    # =====================================================

    grounding_tool = types.Tool(
        google_search=types.GoogleSearch()
    )

    config = types.GenerateContentConfig(
        tools=[
            grounding_tool
        ]
    )


    # =====================================================
    # GEMINI REQUEST
    # =====================================================

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=config
        )

    except Exception as e:

        print(
            "GEMINI API ERROR:",
            repr(e)
        )

        raise


    # =====================================================
    # RESPONSE CHECK
    # =====================================================

    if not response:

        raise RuntimeError(
            "Gemini returned an empty response"
        )

    if not response.text:

        raise RuntimeError(
            "Gemini returned no text in the response"
        )

    return response.text
