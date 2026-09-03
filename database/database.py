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
        .order(
            "id",
            desc=True
        )
        .execute()
    )

    return response.data


# =========================================================
# UPDATE ENQUIRY STATUS
# =========================================================

def update_status(
    item_id,
    status
):

    response = (
        supabase
        .table("enquiries")
        .update({
            "status": status
        })
        .eq(
            "id",
            item_id
        )
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

    destination = destination.strip()
    budget_per_person = float(
        budget_per_person
    )
    days = int(days)


    response = (
        supabase
        .table("travel_packages")
        .select("*")
        .eq(
            "active",
            True
        )
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


    matching_packages = []


    for package in response.data:

        try:

            min_budget = float(
                package.get(
                    "min_budget_per_person",
                    0
                )
            )

            max_budget_value = package.get(
                "max_budget_per_person"
            )

            min_days = int(
                package.get(
                    "min_days",
                    1
                )
            )

            max_days_value = package.get(
                "max_days"
            )


            max_budget = (
                float(max_budget_value)
                if max_budget_value is not None
                else None
            )


            max_days = (
                int(max_days_value)
                if max_days_value is not None
                else None
            )


            budget_ok = (
                budget_per_person >= min_budget
                and
                (
                    max_budget is None
                    or
                    budget_per_person <= max_budget
                )
            )


            days_ok = (
                days >= min_days
                and
                (
                    max_days is None
                    or
                    days <= max_days
                )
            )


            if budget_ok and days_ok:

                matching_packages.append(
                    package
                )


        except (
            TypeError,
            ValueError
        ) as error:

            print(
                "INVALID PACKAGE ROW:",
                item
                if False
                else package
            )

            print(
                "ERROR:",
                repr(error)
            )


    if not matching_packages:
        return None


    matching_packages.sort(
        key=lambda package: float(
            package.get(
                "min_budget_per_person",
                0
            )
        ),
        reverse=True
    )


    return matching_packages[0]


# =========================================================
# FIND NEXT TRAVELVIBE PACKAGE
# =========================================================

def find_next_travel_package(
    destination,
    budget_per_person,
    days
):

    destination = destination.strip()
    budget_per_person = float(
        budget_per_person
    )
    days = int(days)


    response = (
        supabase
        .table("travel_packages")
        .select("*")
        .eq(
            "active",
            True
        )
        .ilike(
            "destination",
            destination
        )
        .order(
            "min_budget_per_person",
            desc=False
        )
        .execute()
    )


    if not response.data:
        return None


    next_package = None


    for package in response.data:

        try:

            min_budget = float(
                package.get(
                    "min_budget_per_person",
                    0
                )
            )

            min_days = int(
                package.get(
                    "min_days",
                    1
                )
            )

            max_days_value = package.get(
                "max_days"
            )

            max_days = (
                int(max_days_value)
                if max_days_value is not None
                else None
            )


            days_ok = (
                days >= min_days
                and
                (
                    max_days is None
                    or
                    days <= max_days
                )
            )


            if (
                days_ok
                and
                min_budget > budget_per_person
            ):

                next_package = package
                break


        except (
            TypeError,
            ValueError
        ) as error:

            print(
                "INVALID NEXT PACKAGE ROW:",
                package
            )

            print(
                "ERROR:",
                repr(error)
            )


    return next_package


# =========================================================
# LIST PLANNER DESTINATIONS
# =========================================================

def list_planner_destinations():

    response = (
        supabase
        .table("planner_destinations")
        .select(
            "id, name, state, description"
        )
        .eq(
            "active",
            True
        )
        .order(
            "name",
            desc=False
        )
        .execute()
    )

    return response.data


# =========================================================
# GET TRAVEL ITINERARY
# =========================================================

def get_travel_itinerary(
    destination,
    budget_per_person,
    days
):

    destination = destination.strip()

    budget_per_person = float(
        budget_per_person
    )

    days = int(days)


    print(
        "========================================"
    )

    print(
        "TRAVELVIBE ITINERARY SEARCH"
    )

    print(
        "Destination:",
        destination
    )

    print(
        "Budget/person:",
        budget_per_person
    )

    print(
        "Days:",
        days
    )

    print(
        "========================================"
    )


    # =====================================================
    # GET ACTIVE ROWS
    # =====================================================

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


    rows = response.data or []


    print(
        "ITINERARY ROW COUNT:",
        len(rows)
    )


    if not rows:

        print(
            "NO ACTIVE ITINERARY ROWS FOUND"
        )

        return []


    matching_rows = []


    # =====================================================
    # FILTER ROWS
    # =====================================================

    for item in rows:

        try:

            row_destination = str(
                item.get(
                    "destination",
                    ""
                )
            ).strip().lower()


            min_budget = float(
                item.get(
                    "min_budget_per_person",
                    0
                )
            )


            max_budget_value = item.get(
                "max_budget_per_person"
            )


            min_days = int(
                item.get(
                    "min_days",
                    1
                )
            )


            max_days_value = item.get(
                "max_days"
            )


            max_budget = (
                float(max_budget_value)
                if max_budget_value is not None
                else None
            )


            max_days = (
                int(max_days_value)
                if max_days_value is not None
                else None
            )


            destination_ok = (
                row_destination
                == destination.lower()
            )


            budget_ok = (
                budget_per_person >= min_budget
                and
                (
                    max_budget is None
                    or
                    budget_per_person <= max_budget
                )
            )


            days_ok = (
                days >= min_days
                and
                (
                    max_days is None
                    or
                    days <= max_days
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
    and
    int(item.get("day_number", 0)) <= days
):
    matching_rows.append(item)


        except (
            TypeError,
            ValueError
        ) as error:

            print(
                "INVALID ITINERARY ROW:",
                item
            )

            print(
                "ERROR:",
                repr(error)
            )


    # =====================================================
    # SORT BY DAY
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
        "MATCHING ITINERARY ROWS:",
        len(matching_rows)
    )


    return matching_rows
