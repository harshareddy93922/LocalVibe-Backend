from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from database.database import create_enquiry, list_enquiries, update_status

router = APIRouter()

class Enquiry(BaseModel):
    name: str
    phone: str
    email: Optional[EmailStr] = None
    destination: Optional[str] = None
    people: Optional[str] = None
    dates: Optional[str] = None
    message: str
    interest: Optional[str] = None

@router.post("/enquiries")
def create(item: Enquiry):
    item_id = create_enquiry(item.model_dump())
    return {"success": True, "id": item_id}

@router.get("/enquiries")
def get_all():
    return {"items": list_enquiries()}

@router.patch("/enquiries/{item_id}/status")
def change_status(item_id: int, status: str):
    allowed = {"NEW", "CONTACTED", "FOLLOW-UP", "CONFIRMED", "COMPLETED"}
    if status not in allowed:
        raise HTTPException(400, "Invalid status")
    update_status(item_id, status)
    return {"success": True}
