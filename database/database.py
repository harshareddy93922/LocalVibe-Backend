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
# FIND EXACT TRAVELVIBE PACKAGE
# =========================================================

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
        .ilike(
            "destination",
            destination
        )
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
        .execute()
    )

    if not response.data:
        return None


    # =====================================================
    # CHECK EACH PACKAGE
    # =====================================================

    for package in response.data:

        min_budget = float(
            package.get(
                "min_budget_per_person",
                0
            )
        )

        max_budget = package.get(
            "max_budget_per_person"
        )

        min_days = int(
            package.get(
                "min_days",
                1
            )
        )

        max_days = package.get(
            "max_days"
        )


        # -------------------------------------------------
        # Budget check
        # -------------------------------------------------

        budget_ok = (
            budget_per_person >= min_budget
            and
            (
                max_budget is None
                or
                budget_per_person <= float(max_budget)
            )
        )


        # -------------------------------------------------
        # Days check
        # -------------------------------------------------

        days_ok = (
            days >= min_days
            and
            (
                max_days is None
                or
                days <= int(max_days)
            )
        )


        # -------------------------------------------------
        # Exact package match
        # -------------------------------------------------

        if budget_ok and days_ok:

            return package


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


        # -------------------------------------------------
        # Maximum budget
        # -------------------------------------------------

        budget_ok = (
            max_budget is None
            or budget_per_person
            <= float(max_budget)
        )


        # -------------------------------------------------
        # Maximum days
        # -------------------------------------------------

        days_ok = (
            max_days is None
            or days
            <= int(max_days)
        )


        # -------------------------------------------------
        # Exact package match
        # -------------------------------------------------

        if budget_ok and days_ok:

            return package


    return None


# =========================================================
# FIND NEXT TRAVELVIBE PACKAGE
# =========================================================
#
# Used when the customer's current budget does not
# match an available package.
#
# Example:
#
# Customer:
# ₹4,000/person
#
# Next package:
# ₹5,000/person
#
# We can then tell the customer the approximate budget
# required instead of simply saying "No".
#
# =========================================================

def find_next_travel_package(
    destination,
    budget_per_person,
    days
):

    response = (
        supabase
        .table("travel_packages")
        .select("*")
        .eq("active", True)
        .ilike(
            "destination",
            destination
        )
        .lte(
            "min_days",
            days
        )
        .order(
            "min_budget_per_person",
            asc=True
        )
        .limit(20)
        .execute()
    )


    if not response.data:
        return None


    # =====================================================
    # FIND CHEAPEST PACKAGE ABOVE CURRENT BUDGET
    # THAT SUPPORTS THE REQUESTED NUMBER OF DAYS
    # =====================================================

    for package in response.data:

        max_days = package.get(
            "max_days"
        )


        # -------------------------------------------------
        # Check maximum days
        # -------------------------------------------------

        days_ok = (
            max_days is None
            or days
            <= int(max_days)
        )


        if not days_ok:
            continue


        # -------------------------------------------------
        # Package minimum budget
        # -------------------------------------------------

        min_budget = float(
            package.get(
                "min_budget_per_person",
                0
            )
        )


        # -------------------------------------------------
        # Only return a package that costs more than
        # the customer's current budget.
        # -------------------------------------------------

        if min_budget > budget_per_person:

            return package


    return None
    # =========================================================
# LIST PLANNER DESTINATIONS
# =========================================================

def list_planner_destinations():

    response = (
        supabase
        .table("planner_destinations")
        .select("id, name, state")
        .eq("active", True)
        .order("name")
        .execute()
    )

    return response.data
    # =========================================================
# GET TRAVEL ITINERARY
# =========================================================

# =========================================================
# GET TRAVEL ITINERARY
# =========================================================

# =========================================================
# GET TRAVEL ITINERARY
# =========================================================

# =========================================================
# GET TRAVEL ITINERARY
# =========================================================

# =========================================================
# GET TRAVEL ITINERARY
# =========================================================

def get_travel_itinerary(
    destination,
    budget_per_person,
    days
):

    destination = destination.strip()
    budget_per_person = float(budget_per_person)
    days = int(days)

    print("========================================")
    print("TRAVELVIBE ITINERARY DEBUG")
    print("Destination:", destination)
    print("Budget/person:", budget_per_person)
    print("Days:", days)
    print("========================================")


    # -----------------------------------------------------
    # Fetch destination rows
    # -----------------------------------------------------

    response = (
        supabase
        .table("travel_itineraries")
        .select("*")
        .eq(
            "active",
            True
        )
        .execute()
    )


    print(
        "TOTAL ITINERARY ROWS RETURNED:",
        len(response.data or [])
    )

    print(
        "ALL ITINERARY DATA:",
        response.data
    )


    if not response.data:

        print(
            "NO ROWS FOUND IN travel_itineraries"
        )

        return []


    matching_rows = []


    # =====================================================
    # FILTER IN PYTHON
    # =====================================================

    for item in response.data:

        row_destination = str(
            item.get(
                "destination",
                ""
            )
        ).strip().lower()


        row_min_budget = float(
            item.get(
                "min_budget_per_person",
                0
            )
        )


        row_max_budget_value = item.get(
            "max_budget_per_person"
        )


        row_min_days = int(
            item.get(
                "min_days",
                1
            )
        )


        row_max_days_value = item.get(
            "max_days"
        )


        row_max_budget = (

            float(row_max_budget_value)

            if row_max_budget_value is not None

            else None

        )


        row_max_days = (

            int(row_max_days_value)

            if row_max_days_value is not None

            else None

        )


        destination_ok = (
            row_destination ==
            destination.lower()
        )


        budget_ok = (
            budget_per_person >=
            row_min_budget
            and
            (
                row_max_budget is None
                or
                budget_per_person <=
                row_max_budget
            )
        )


        days_ok = (
            days >= row_min_days
            and
            (
                row_max_days is None
                or
                days <= row_max_days
            )
        )


        print(
            "ROW:",
            item.get("id"),
            "| destination:",
            destination_ok,
            "| budget:",
            budget_ok,
            "| days:",
            days_ok
        )


        if (
            destination_ok
            and
            budget_ok
            and
            days_ok
        ):

            matching_rows.append(
                item
            )


    # =====================================================
    # SORT
    # =====================================================

    matching_rows.sort(
        key=lambda item: int(
            item.get(
                "day_number",
                0
            )
        )
    )


    print(
        "FINAL MATCHING ITINERARY ROWS:",
        len(matching_rows)
    )


    return matching_rows
