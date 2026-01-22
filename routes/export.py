from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session
from database.database import get_db

from models import *

from utils.csv import generate_csv

router = APIRouter(
    prefix="/export",
    tags=["Export"]
)

@router.get("/{select}")
def export_csv(select: str, db: Session = Depends(get_db)):
    
    selects = {
        "users": User,
        "projects": Project,
        "skills": Skill,
        "volunteers": Volunteer,
        "assignments": Assignment,
        "categories": Category,
        "role": Role
    }
    
    if select not in selects:
        return Response(status_code=404, detail="Select not found")
    
    model = selects[select]
    
    results = db.query(model).all()
    print("RESULTADOS:", results)
    print("TOTAL:", len(results))

    
    if not results:
        return Response(status_code=404, detail="Data export not found")
    
    rows =[
        {col.name: getattr(obj, col.name) for col in model.__table__.columns}
        for obj in results
    ]
    
    csv_data = generate_csv(rows)
    
    return Response(content="\ufeff" + csv_data,
                    media_type="text/csv",
                    headers={
                        "Content-Disposition": f"attachment; filename={select}.csv"
                        }
                    )