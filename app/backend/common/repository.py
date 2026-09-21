from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.backend.core.exceptions import NotFoundError

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    model: type[ModelType]

    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, instance: ModelType) -> ModelType:
        self.session.add(instance)
        self.session.flush()
        self.session.refresh(instance)
        return instance

    def get(self, entity_id: str) -> ModelType:
        instance = self.session.get(self.model, entity_id)
        if not instance:
            raise NotFoundError(f"{self.model.__name__} with id '{entity_id}' was not found.")
        return instance

    def list(self) -> list[ModelType]:
        return list(self.session.scalars(select(self.model)))

    def delete(self, instance: ModelType) -> None:
        self.session.delete(instance)
