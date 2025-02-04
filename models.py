# models.py
from sqlalchemy import Table, Column, Integer, String, Boolean, MetaData, TIMESTAMP, Date, ForeignKey, Text

metadata = MetaData()

cursos = Table(
    "cursos",
    metadata,
    Column("curso_id", Integer, primary_key=True),
    Column("nombre", String(100)),
    Column("descripcion", Text),
    Column("indice", Integer),
    Column("codigo_ensenanza", Integer),
    Column("profesor_jefe_id", Integer, ForeignKey("usuarios.usuario_id")),
    Column("fecha_creacion", TIMESTAMP),
    Column("fecha_actualizacion", TIMESTAMP),
)

estudiantes = Table(
    "estudiantes",
    metadata,
    Column("estudiante_id", Integer, primary_key=True),
    Column("nombre", String(100)),
    Column("rut", String(100), unique=True),
    Column("curso_id", Integer, ForeignKey("cursos.curso_id", ondelete="CASCADE")),
    Column("numlista", Integer),
    Column("email", String(150), unique=True),
    Column("clave_email", String(250)),
    Column("clave", String(250)),
    Column("fecha_creacion", TIMESTAMP),
    Column("fecha_actualizacion", TIMESTAMP),
    Column("fecha_nacimiento", Date),
    Column("fecha_ingreso", Date),
    Column("activo", Boolean, default=True),
)