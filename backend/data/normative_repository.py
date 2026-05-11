"""IRepoNormativo — config store: normative source catalog (RF01)."""

import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from agente.data.database import Base


class PaisEnum(str, enum.Enum):
    AR = "AR"
    UY = "UY"


class TipoDocumentoEnum(str, enum.Enum):
    ley = "ley"
    decreto = "decreto"
    resolucion = "resolucion"
    ordenanza = "ordenanza"
    reglamento = "reglamento"
    circular = "circular"
    otro = "otro"


class ClasificacionEnum(str, enum.Enum):
    oficial = "oficial"
    secundaria = "secundaria"
    auxiliar = "auxiliar"


class FuenteNormativa(Base):
    __tablename__ = "fuentes_normativas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    pais: Mapped[PaisEnum] = mapped_column(Enum(PaisEnum), nullable=False)
    organismo: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo_documento: Mapped[TipoDocumentoEnum] = mapped_column(Enum(TipoDocumentoEnum), nullable=False)
    clasificacion: Mapped[ClasificacionEnum] = mapped_column(Enum(ClasificacionEnum), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    historial: Mapped[list["HistorialFuente"]] = relationship(
        "HistorialFuente", back_populates="fuente", lazy="select"
    )


class HistorialFuente(Base):
    __tablename__ = "historial_fuentes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fuente_id: Mapped[int] = mapped_column(Integer, ForeignKey("fuentes_normativas.id"), nullable=False)
    nuevo_estado: Mapped[bool] = mapped_column(Boolean, nullable=False)
    motivo: Mapped[str | None] = mapped_column(String(500), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    fuente: Mapped["FuenteNormativa"] = relationship("FuenteNormativa", back_populates="historial")


class NormativeRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create_fuente(self, data: dict) -> FuenteNormativa:
        fuente = FuenteNormativa(**data)
        self._db.add(fuente)
        self._db.commit()
        self._db.refresh(fuente)
        return fuente

    def get_fuentes(
        self,
        pais: PaisEnum | None = None,
        clasificacion: ClasificacionEnum | None = None,
        activo: bool | None = None,
    ) -> list[FuenteNormativa]:
        query = self._db.query(FuenteNormativa)
        if pais is not None:
            query = query.filter(FuenteNormativa.pais == pais)
        if clasificacion is not None:
            query = query.filter(FuenteNormativa.clasificacion == clasificacion)
        if activo is not None:
            query = query.filter(FuenteNormativa.activo == activo)
        return query.all()

    def get_fuente_by_id(self, fuente_id: int) -> FuenteNormativa | None:
        return self._db.get(FuenteNormativa, fuente_id)

    def toggle_estado(self, fuente: FuenteNormativa, motivo: str | None = None) -> FuenteNormativa:
        fuente.activo = not fuente.activo
        fuente.updated_at = datetime.utcnow()
        entrada = HistorialFuente(fuente_id=fuente.id, nuevo_estado=fuente.activo, motivo=motivo)
        self._db.add(entrada)
        self._db.commit()
        self._db.refresh(fuente)
        return fuente

    def get_historial(self, fuente_id: int) -> list[HistorialFuente]:
        return (
            self._db.query(HistorialFuente)
            .filter(HistorialFuente.fuente_id == fuente_id)
            .order_by(HistorialFuente.timestamp.desc())
            .all()
        )

    def seed(self) -> None:
        if self._db.query(FuenteNormativa).count() > 0:
            return
        from backend.modules.ingestion.sources_config import FUENTES_SEMILLA

        fuentes = [FuenteNormativa(**f) for f in FUENTES_SEMILLA]
        self._db.add_all(fuentes)
        self._db.commit()
