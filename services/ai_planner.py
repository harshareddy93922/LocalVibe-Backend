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

    # -----------------------------------------------------
    # Package information
    # -----------------------------------------------------

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

Your job is to create a useful and realistic travel
experience for the traveller.

IMPORTANT:

You have access to Google Search.

Use Google Search when you need information about:

- the destination
- attractions
- local culture
- local food
- activities
- travel conditions
- places to visit
- publicly available destination information
- current information that may have changed

Do NOT assume that a destination must exist in the
TravelVibe database.

A destination can be planned even when TravelVibe does
not yet have a predefined package for it.


=========================================================
TRAVELLER DETAILS
=========================================================

Destination:
{destination}

Travellers:
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
TRAVELVIBE DATABASE INFORMATION
=========================================================

Available TravelVibe experience:

{experience}

Included TravelVibe services:

{inclusions_text}


=========================================================
IMPORTANT RULES
=========================================================

1. Use Google Search to research the destination when
   necessary.

2. Do NOT invent destination facts.

3. Do NOT invent hotel availability.

4. Do NOT invent booking confirmations.

5. Do NOT claim that TravelVibe has a local partner unless
   that information was provided.

6. Do NOT invent exact prices.

7. If current public prices are found through Google Search,
   clearly describe them as publicly listed or approximate.

8. Do NOT guarantee that the complete trip will fit the
   requested budget unless the available information
   supports that conclusion.

9. The customer's budget is the PRIMARY constraint.

10. Prefer affordable and authentic experiences.

11. Prefer local food, local culture, nature, villages,
    local stays and community experiences when relevant.

12. If the destination has no TravelVibe package, still
    create a useful suggested itinerary.

13. Clearly tell the traveller that TravelVibe will confirm
    final prices, availability and arrangements.

14. Never expose internal database information or package
    names.

15. Do not stop simply because no TravelVibe package exists.


=========================================================
CREATE THE RESPONSE
=========================================================

Create a personalized itinerary.

Use this format:


🌴 YOUR TRAVELVIBE

A short welcoming sentence.


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

Continue for additional days.


🍛 What You Can Experience

List the most relevant experiences.


💰 Your Budget

Explain how the suggested experience relates to the
traveller's requested budget.

Do NOT invent a detailed cost breakdown unless reliable
pricing information is available.


🌿 Why This Fits Your Vibe

Explain how the itinerary matches the traveller's
interests.


🤝 What Happens Next

Tell the traveller that TravelVibe will confirm the final
itinerary, availability, exact prices and arrangements.


Finish with:

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

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=config
    )


    # =====================================================
    # SAFETY CHECK
    # =====================================================

    if not response.text:

        return (
            "We couldn't generate your TravelVibe plan "
            "right now. Please try again."
        )


    return response.text
