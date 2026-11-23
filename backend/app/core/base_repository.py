from typing import Generic, TypeVar

from sqlalchemy import func
from sqlmodel import SQLModel, Session, select

T = TypeVar("T", bound=SQLModel)


class BaseRepository(Generic[T]):
    def __init__(self, session: Session, model: type[T]):
        self.session = session
        self.model = model

    def get_by_id(self, identifier: int) -> T | None:
        return self.session.get(self.model, identifier)

    def get_all(self) -> list[T]:
        return list(self.session.exec(select(self.model).order_by(self.model.id)).all())

    def add(self, obj: T) -> T:
        self.session.add(obj)
        self.session.flush()
        return obj

    def delete(self, obj: T) -> None:
        self.session.delete(obj)

    def page(self, statement, skip: int, limit: int):
        total = self.session.exec(
            select(func.count()).select_from(statement.subquery())
        ).one()
        return total, list(self.session.exec(statement.offset(skip).limit(limit)).all())
