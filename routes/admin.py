from fastapi import APIRouter, Header, HTTPException
router=APIRouter()

@router.post("/admin/login")
def login(email:str,password:str):
    if email=="admin@localvibe.test" and password=="localvibe123":
        return {"success":True,"token":"demo-token-change-before-production"}
    raise HTTPException(status_code=401,detail="Invalid credentials")
