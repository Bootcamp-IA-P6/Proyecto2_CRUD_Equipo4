import csv 
from io import StringIO

def generate_csv(rows: list[dict]) -> str:
    """
    Genera un archivo CSV a partir de una lista de diccionarios.
    """
    if not rows:
        return ""
    
    buffer = StringIO()
    writer = csv.writer(buffer)
    #encabezados
    writer.writerow(rows[0].keys())
    #filas
    for row in rows:
        writer.writerow(row.values())
    return buffer.getvalue()