from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base


class WarehouseTable(Base):
    __tablename__ = "warehouse_tables"

    id: Mapped[int] = mapped_column(primary_key=True)
    database_name: Mapped[str] = mapped_column(String(255), index=True)
    schema_name: Mapped[str] = mapped_column(String(255), index=True)
    table_name: Mapped[str] = mapped_column(String(255), index=True)
    table_type: Mapped[str] = mapped_column(String(100), default="BASE TABLE")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
