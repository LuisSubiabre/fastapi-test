from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/saludar/{nombre}")
def saludar(nombre: str):
    if nombre == "Luis":
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return {"message": "¡Hola, Luis! ¿Cómo estás?"}


class Item(BaseModel):
    nombre: str
    descripcion: str = None
    precio: float
    impuesto: float = None

@app.post("/items/")
def create_item(item: Item):
    return {"item": item}

