from fastapi import APIRouter
router=APIRouter()

@router.get("/destinations")
def get_destinations():
    return [
      {"name":"Kodaikanal Slow Escape","state":"Tamil Nadu","type":"Hill Station"},
      {"name":"Thanjavur & the Big Temple","state":"Tamil Nadu","type":"Temple + Heritage"},
      {"name":"Andhra Village Stories","state":"Andhra Pradesh","type":"Local Villages"},
      {"name":"Hampi With Local Stories","state":"Karnataka","type":"Heritage"},
      {"name":"Wayanad Village Walk","state":"Kerala","type":"Village + Nature"},
      {"name":"Valparai Offbeat Escape","state":"Tamil Nadu","type":"Tea + Hills"}
    ]
