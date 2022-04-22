from typing import TypeVar, Generic, Type, Optional, Tuple, Any
from tortoise.models import Model
from loguru import logger

ModelType = TypeVar("ModelType", bound=Model)


class CRUDBase(Generic[ModelType]):
    __slots__ = ("model",)

    def __init__(self, model: Type[ModelType]):
        self.model = model

    def show_info(self, return_model: Type[ModelType]) -> None:
        logger.info(f"[{self.model.__name__}]::{return_model}")

    async def create(self, **kwargs: Any) -> ModelType:
        _model = await self.model.create(**kwargs)
        self.show_info(_model)
        return _model

    async def get(self, prefetch: Tuple[str] = None, **kwargs) -> Optional[ModelType]:
        if prefetch:
            _model = (
                await self.model.filter(**kwargs).prefetch_related(*prefetch).first()
            )
        else:
            _model = await self.model.filter(**kwargs).first()
        self.show_info(_model)
        return _model

    async def get_all(
        self, *, offset: int = 0, limit: int = 100, prefetch: Tuple[str] = None
    ) -> ModelType:
        if prefetch:
            _model = (
                await self.model.all()
                .offset(offset)
                .limit(limit)
                .prefetch_related(*prefetch)
            )
        else:
            _model = await self.model.all().offset(offset).limit(limit)
        self.show_info(_model)
        return _model
