# main.py
from fastapi import FastAPI, HTTPException, Path, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from databases import Database
from sqlalchemy.sql import select, join
from models import estudiantes, cursos, metadata
from config import DATABASE_URL
from auth import (
    verify_password,
    create_access_token,
    decode_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_password_hash,oauth2_scheme
)
from pydantic import BaseModel

# Configuración de la aplicación FastAPI
app = FastAPI()

# Configuración de la base de datos
database = Database(DATABASE_URL)

class LoginRequest(BaseModel):
    email: str
    clave: str

# Eventos de inicio y cierre de la aplicación
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Función para obtener un estudiante por su email
async def get_student(email: str):
    query = estudiantes.select().where(estudiantes.c.email == email)
    student = await database.fetch_one(query)
    if student:
        return student
    return None

# Ruta de login
@app.post("/login")
async def login(login_data: LoginRequest):
    student = await get_student(login_data.email)  # Usamos el email del cuerpo JSON
    if not student or not verify_password(login_data.clave, student["clave"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Crear el token JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Obtener el nombre del curso
    query = select(cursos.c.nombre).where(cursos.c.curso_id == student["curso_id"])
    curso = await database.fetch_one(query)
    curso_nombre = curso["nombre"] if curso else None

    access_token = create_access_token(
        data={
            "sub": student["email"],
            "estudiante_id": student["estudiante_id"],
            "nombre": student["nombre"],
            "curso": student["curso_id"],
            "curso_nombre": curso_nombre,
        },
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}

# Ruta protegida (ejemplo)
@app.get("/protegido")
async def ruta_protegida(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)  # Decodificar el token
    return {
        "message": "Acceso concedido",
        "user_email": payload["sub"],
        "estudiante_id": payload["estudiante_id"],
        "nombre": payload["nombre"],
    }

# Endpoint para obtener un estudiante por su ID
@app.get("/estudiante/{id}", response_model=dict)
async def obtener_estudiante(
    id: int = Path(..., description="El ID del estudiante")
):
    # Crear la consulta con JOIN entre estudiantes y cursos
    query = (
        select(
            estudiantes.c.estudiante_id,
            estudiantes.c.nombre,
            estudiantes.c.rut,
            estudiantes.c.curso_id,
            estudiantes.c.numlista,
            estudiantes.c.email,
            estudiantes.c.activo,
            cursos.c.nombre.label("curso_nombre"),
        )
        .select_from(
            join(estudiantes, cursos, estudiantes.c.curso_id == cursos.c.curso_id)
        )
        .where(estudiantes.c.estudiante_id == id)
    )

    # Ejecutar la consulta
    result = await database.fetch_one(query)

    # Si no se encuentra el estudiante, lanzar un error 404
    if not result:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    # Formatear la respuesta
    estudiante_info = {
        "estudiante_id": result["estudiante_id"],
        "nombre": result["nombre"],
        "rut": result["rut"],
        "curso_id": result["curso_id"],
        "curso_nombre": result["curso_nombre"],
        "numlista": result["numlista"],
        "activo": result["activo"],
        "href": f"http://localhost:8000/estudiante/{result['estudiante_id']}",
    }

    return {"data": estudiante_info}