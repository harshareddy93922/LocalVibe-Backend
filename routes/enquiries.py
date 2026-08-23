import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")

if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
    raise RuntimeError("Supabase environment variables are missing")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SECRET_KEY
)


def init_db():
    pass


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
        raise RuntimeError("Failed to create enquiry")

    return response.data[0]["id"]


def list_enquiries():
    response = (
        supabase
        .table("enquiries")
        .select("*")
        .order("id", desc=True)
        .execute()
    )

    return response.data


def update_status(item_id, status):
    response = (
        supabase
        .table("enquiries")
        .update({"status": status})
        .eq("id", item_id)
        .execute()
    )

    return response.data
