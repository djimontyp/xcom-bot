from enum import StrEnum

from discord import (
    Cog,
    ApplicationContext,
    SlashCommandGroup,
    Role,
    TextChannel,
    Option,
    AutocompleteContext,
    OptionChoice,
)
from discord.ext.commands import Bot

from src import database
from src.config import settings
from src.services.roles import RolesService


class Rank(StrEnum):
    neofit = "Неофит"
    adept = "Адепт"
    master = "Мастер"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


async def ranks_options(ctx: AutocompleteContext):
    return [OptionChoice(name=rank, value=rank) for rank in Rank.list()]


class AdminCog(Cog, guild_ids=[settings.GUILD_ID]):
    def __init__(self, bot: Bot):
        self.bot = bot

    admin = SlashCommandGroup("admin", "Группа команд для администраторов.")

    @admin.command(description="Установить роли соответствия для рангов.")
    async def set_roles(self, ctx: ApplicationContext, neofit: Role | None, adept: Role | None, master: Role | None):
        await ctx.defer()

        roles_service = RolesService()

        roles_service.update(neofit=neofit.id) if neofit else ...
        roles_service.update(adept=adept.id) if adept else ...
        roles_service.update(master=master.id) if master else ...

        embed = roles_service.get_embed("Роли обновлены.")
        await ctx.respond(embed=embed, delete_after=30, ephemeral=True)

    @admin.command(description="Установить канал для поиска сессии.")
    async def set_session_channel(self, ctx: ApplicationContext, channel: TextChannel):
        await ctx.defer()
        database.session_channel = channel.id
        await ctx.respond(f"Канал для поиска сессии установлен на {channel.mention}.", delete_after=30, ephemeral=True)

    @admin.command(description="Показать канал для поиска сессии.")
    async def session_channel(self, ctx: ApplicationContext):
        await ctx.defer()

        if channel := ctx.guild.get_channel(database.session_channel):
            await ctx.respond(f"Канал поиска сессии: {channel.mention}.", delete_after=30, ephemeral=True)
        else:
            await ctx.respond(f"Канал поиска сессии не найден.", delete_after=30, ephemeral=True)

    @admin.command(description="Показать установленные роли соответствия для рангов.")
    async def roles(self, ctx: ApplicationContext):
        await ctx.defer()
        embed = RolesService().get_embed()
        await ctx.respond(embed=embed, delete_after=30, ephemeral=True)

    @admin.command()
    async def session_message(self, ctx: ApplicationContext, rank: Option(autocomplete=ranks_options)):
        await ctx.defer()

        await ctx.respond(f"Канал поиска сессии не найден. {rank}", delete_after=30, ephemeral=True)
