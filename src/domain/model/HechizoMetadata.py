
from pydantic import BaseModel, Field

class HechizoMetadata(BaseModel):
    nivel: int = Field(description="Nivel del hechizo del 1 al 9")
    clases: str = Field(description="Clases que pueden usarlo, ej: Mago, Clérigo")
    nombre: str = Field(description="Nombre oficial del hechizo")
    componentes: str = Field(description="Componentes necesarios: verbal, somático, material")
    duracion: str = Field(description="Duración del efecto")
    tiempo_lanzamiento: str = Field(description="Tiempo necesario para lanzar el hechizo")