# cogs/moderacao.py

from discord.ext import commands

class ModeracaoCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Futuramente, os seus comandos de moderação virão aqui.
    # Exemplo: @commands.command()


# A função setup que o bot procura em cada ficheiro de Cog.
async def setup(bot: commands.Bot):
    await bot.add_cog(ModeracaoCog(bot))