"""AdminController — IIngestionManager: normative source catalog management."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.data.database import get_db
from backend.data.normative_repository import ClasificacionEnum, NormativeRepository, PaisEnum
from backend.schemas.fuente import (
    FuenteCreate,
    FuenteListResponse,
    FuenteRead,
    HistorialEntrada,
    ToggleEstadoRequest,
)

router = APIRouter(prefix="/admin/fuentes", tags=["admin"])


@router.get("/", response_model=FuenteListResponse)
def list_fuentes(
    pais: PaisEnum | None = None,
    clasificacion: ClasificacionEnum | None = None,
    activo: bool | None = None,
    db: Session = Depends(get_db),
) -> FuenteListResponse:
    repo = NormativeRepository(db)
    items = repo.get_fuentes(pais=pais, clasificacion=clasificacion, activo=activo)
    return FuenteListResponse(items=items, total=len(items))


@router.post("/", response_model=FuenteRead, status_code=201)
def create_fuente(body: FuenteCreate, db: Session = Depends(get_db)) -> FuenteRead:
    repo = NormativeRepository(db)
    fuente = repo.create_fuente(body.model_dump())
    return FuenteRead.model_validate(fuente)


@router.get("/{fuente_id}", response_model=FuenteRead)
def get_fuente(fuente_id: int, db: Session = Depends(get_db)) -> FuenteRead:
    repo = NormativeRepository(db)
    fuente = repo.get_fuente_by_id(fuente_id)
    if fuente is None:
        raise HTTPException(status_code=404, detail="Fuente normativa no encontrada")
    return FuenteRead.model_validate(fuente)


@router.patch("/{fuente_id}/estado", response_model=FuenteRead)
def toggle_estado(fuente_id: int, body: ToggleEstadoRequest, db: Session = Depends(get_db)) -> FuenteRead:
    repo = NormativeRepository(db)
    fuente = repo.get_fuente_by_id(fuente_id)
    if fuente is None:
        raise HTTPException(status_code=404, detail="Fuente normativa no encontrada")
    fuente = repo.toggle_estado(fuente, motivo=body.motivo)
    return FuenteRead.model_validate(fuente)


@router.get("/{fuente_id}/historial", response_model=list[HistorialEntrada])
def get_historial(fuente_id: int, db: Session = Depends(get_db)) -> list[HistorialEntrada]:
    repo = NormativeRepository(db)
    if repo.get_fuente_by_id(fuente_id) is None:
        raise HTTPException(status_code=404, detail="Fuente normativa no encontrada")
    return repo.get_historial(fuente_id)
