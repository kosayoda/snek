import logging
from datetime import datetime
from typing import Optional

import discord
import humanize
from discord import TextChannel
from discord.ext.commands import Cog, Context, group

from snek.bot import Snek
from snek.utils.converters import DurationDelta

log = logging.getLogger(__name__)

SLOWMODE_MAX_DELAY = 21600  # seconds


class Slowmode(Cog):
    """Commands for getting and setting slowmode delays of text channels."""

    def __init__(self, bot: Snek) -> None:
        self.bot = bot

    @group(name='slowmode', aliases=['sm'], invoke_without_command=True)
    async def slowmode_group(self, ctx: Context) -> None:
        """Get or set the slowmode delay for the text channel this was invoked in or a given text channel."""
        await ctx.send_help(ctx.command)

    @slowmode_group.command(name='get', aliases=['g'])
    async def get_slowmode(self, ctx: Context, channel: Optional[TextChannel]) -> None:
        """Get the slowmode delay for a text channel."""
        # Use the channel this command was invoked in if one was not given
        if channel is None:
            channel = ctx.channel

        humanized_delay = humanize.precisedelta(channel.slowmode_delay, minimum_unit='seconds', format=r'%0.0f')

        await ctx.send(f'The slowmode delay for {channel.mention} is {humanized_delay}.')

    @slowmode_group.command(name='set', aliases=['s'])
    async def set_slowmode(self, ctx: Context, channel: Optional[TextChannel], delay: DurationDelta) -> None:
        """Set the slowmode delay for a text channel."""
        # Use the channel this command was invoked in if one was not given
        if channel is None:
            channel = ctx.channel

        # Convert `dateutil.relativedelta.relativedelta` to `datetime.timedelta`
        # Must do this to get the delta in a particular unit of time
        utcnow = datetime.utcnow()
        slowmode_delay = (utcnow + delay - utcnow).total_seconds()

        humanized_delay = humanize.precisedelta(slowmode_delay, minimum_unit='seconds', format=r'%0.0f')

        # Ensure the delay is within discord's limits
        if slowmode_delay <= SLOWMODE_MAX_DELAY:
            log.info(f'{ctx.author} set the slowmode delay for #{channel} to {humanized_delay}.')

            await channel.edit(slowmode_delay=slowmode_delay)
            await ctx.send(
                f'✅ The slowmode delay for {channel.mention} is now {humanized_delay}.'
            )

        else:
            log.info(
                f'{ctx.author} tried to set the slowmode delay of #{channel} to {humanized_delay}, '
                'which is not between 0 and 6 hours.'
            )

            await ctx.send(
                '❌ The slowmode delay must be between 0 and 6 hours.'
            )

    @slowmode_group.command(name='reset', aliases=['r'])
    async def reset_slowmode(self, ctx: Context, channel: Optional[TextChannel]) -> None:
        """Reset the slowmode delay for a text channel to 0 seconds."""
        # Use the channel this command was invoked in if one was not given
        if channel is None:
            channel = ctx.channel

        log.info(f'{ctx.author} reset the slowmode delay for #{channel} to 0 seconds.')

        await channel.edit(slowmode_delay=0)
        await ctx.send(
            f'✅ The slowmode delay for {channel.mention} has been reset to 0 seconds.'
        )

    async def cog_check(self, ctx: Context) -> bool:
        """Only allow moderators to invoke the commands in this cog."""
        return discord.utils.get(ctx.author.roles, id=self.bot.configs[ctx.guild.id]['mod_role'])


def setup(bot: Snek) -> None:
    """Load the Slowmode cog."""
    bot.add_cog(Slowmode(bot))
