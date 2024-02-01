# -----------------------------------------------------------------------------
# Абстрактный класс. Не использовать напрямую.
import asyncio
from abc import ABC
from functools import cached_property
from typing import Any, Mapping

import discord
from sqlalchemy import BinaryExpression, update, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.baked import Result

from src.core.database import async_session_maker


class Service(ABC):
    model: Any = None

    instance: Any = None
    session: AsyncSession | None = None

    def __init__(
        self,
        entity_id: int | None = None,
        /,
        interaction: discord.Interaction = None,
        ctx: discord.ApplicationContext = None,
    ):
        self.entity_id = entity_id
        self.ctx = ctx
        self.interaction = interaction if interaction else ctx.interaction
        self.guild = ctx.guild if ctx else interaction.guild

    async def __aenter__(self):
        self.session: AsyncSession = async_session_maker()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        task = asyncio.create_task(self.session.close())
        await asyncio.shield(task)
        self.session = None

    @cached_property
    def criteria(self) -> BinaryExpression:
        return self.model.id == self.entity_id

    async def update(self, **kwargs) -> None:
        stmt = update(self.model).where(self.criteria).values(**kwargs)
        await self.session.execute(stmt)

    async def get_instance(self, *options, **filters: Mapping[str, Any]) -> Result:
        stmt = select(self.model).options(*options).where(self.criteria)
        if filters:
            stmt = stmt.where(**filters)

        self.instance.service = self
        self.instance = await self.session.scalar(stmt)
        return self.instance
