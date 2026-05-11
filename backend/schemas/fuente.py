from datetime import datetime

from pydantic import BaseModel, ConfigDict

from backend.data.normative_repository import ClasificacionEnum, PaisEnum, TipoDocumentoEnum


class FuenteBase(BaseModel):
    nombre: str
    pais: PaisEnum
    organismo: str
    tipo_documento: TipoDocumentoEnum
    clasificacion: ClasificacionEnum
    url: str


class FuenteCreate(FuenteBase):
    pass


class FuenteRead(FuenteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    activo: bool
    created_at: datetime
    updated_at: datetime


class HistorialEntrada(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fuente_id: int
    nuevo_estado: bool
    motivo: str | None
    timestamp: datetime


class ToggleEstadoRequest(BaseModel):
    motivo: str | None = None


class FuenteListResponse(BaseModel):
    items: list[FuenteRead]
    total: int
