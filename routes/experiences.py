from fastapi import APIRouter
router=APIRouter()

@router.get("/experiences")
def get_experiences():
    return [
      {"name":"Eat Like a Local","category":"Food"},
      {"name":"Temple & Culture","category":"Culture"},
      {"name":"Village Stories","category":"Village"},
      {"name":"Meet & Mingle","category":"Social"}
    ]
