import os

from supabase import create_client, Client


# =========================================================
# SUPABASE CONNECTION
# =========================================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")


if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
    raise RuntimeError(
        "Supabase environment variables are missing"
    )


supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SECRET_KEY
)


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def init_db():
    pass


# =========================================================
# CREATE ENQUIRY
# =========================================================

def create_enquiry(data):

    response = (
        supabase
        .table("enquiries")
        .insert({
            "name": data["name"],
            "phone": data["phone"],
            "email": data.get("email"),
            "destination": data.get("destination"),
            "people": data.get("people"),
            "dates": data.get("dates"),
            "message": data["message"],
            "interest": data.get("interest"),
            "status": "NEW"
        })
        .execute()
    )

    if not response.data:
        raise RuntimeError(
            "Failed to create enquiry"
        )

    return response.data[0]["id"]


# =========================================================
# LIST ENQUIRIES
# =========================================================

def list_enquiries():

    response = (
        supabase
        .table("enquiries")
        .select("*")
        .order("id", desc=True)
        .execute()
    )

    return response.data


# =========================================================
# UPDATE ENQUIRY STATUS
# =========================================================

def update_status(item_id, status):

    response = (
        supabase
        .table("enquiries")
        .update({
            "status": status
        })
        .eq("id", item_id)
        .execute()
    )

    return response.data


# =========================================================
# FIND TRAVELVIBE PACKAGE
# =========================================================

def find_travel_package(
    destination,
    budget_per_person,
    days
):

    response = (
        supabase
        .table("travel_packages")
        .select("*")
        .eq("active", True)
        .ilike("destination", destination)
        .lte(
            "min_budget_per_person",
            budget_per_person
        )
        .lte(
            "min_days",
            days
        )
        .order(
            "min_budget_per_person",
            desc=True
        )
        .limit(10)
        .execute()
    )


    if not response.data:
        return None


    # =====================================================
    # CHECK PACKAGE LIMITS
    # =====================================================

    for package in response.data:

        max_budget = package.get(
            "max_budget_per_person"
        )

        max_days = package.get(
            "max_days"
        )


        # Check maximum budget

        budget_ok = (
            max_budget is None
            or budget_per_person
            <= float(max_budget)
        )


        # Check maximum days

        days_ok = (
            max_days is None
            or days
            <= int(max_days)
        )


        # If both conditions match

        if budget_ok and days_ok:

            return package


    return None
