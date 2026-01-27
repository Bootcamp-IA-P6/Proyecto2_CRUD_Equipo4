from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.database.database import get_db
from enum import Enum
from app.models import *

from app.utils.csv import generate_csv

router = APIRouter(
    prefix="/export",
    tags=["Export"]
)

class SelectEnum(str, Enum):
    users = "users"
    projects = "projects"
    skills = "skills"
    volunteers = "volunteers"
    assignments = "assignments"
    categories = "categories"
    role = "role"


@router.get("/{select}")
def export_csv(select: SelectEnum, db: Session = Depends(get_db)):
    """
    ## Exportación de datos a CSV por selección.

    Este endpoint permite descargar datos de diferentes entidades de la aplicación
    en formato CSV, listos para abrir en Excel o cualquier editor de hojas de cálculo.

    ### Uso

    **URL:** `/export/{select}`  
    **Método:** GET  
    **Parámetros de ruta:**
    - `select` (str): La categoría de datos que quieres exportar. Valores válidos:
    - `users` → Usuarios
    - `projects` → Proyectos
    - `skills` → Habilidades
    - `volunteers` → Voluntarios
    - `assignments` → Asignaciones
    - `categories` → Categorías
    - `role` → Roles de usuario

    ### Ejemplo de llamada
    ```bash
    curl -X GET http://localhost:8000/export/users -o users.csv
    ```

    ### Respuesta
    - Archivo CSV con encabezados automáticos
    - Cada fila corresponde a un registro de la tabla seleccionada
    - Codificación UTF-8 con BOM para compatibilidad con Excel
    - Nombre del archivo: `{select}.csv` (por ejemplo `users.csv`)

    ### Notas
    - Si la categoría no existe, devuelve un **404 Not Found**.
    - Si no hay registros, devuelve un **404 Data export not found**.
    """
    
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