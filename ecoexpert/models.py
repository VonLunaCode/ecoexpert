from typing import Literal
from pydantic import BaseModel, ConfigDict


class Consulta(BaseModel):
    model_config = ConfigDict(extra="forbid")
    objeto: Literal["restos_comida", "botella_plastico", "caja_carton", "hojas_papel", "frasco_vidrio", "lata", "celular", "laptop", "otro", "desconocido"] = "desconocido"
    limpio: Literal["si", "no", "desconocido"] | None = None
    contacto_quimicos: Literal["si", "no", "desconocido"] = "desconocido"
