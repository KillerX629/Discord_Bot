from discord.ext import commands


def setup(bot):
    bot.add_cog(testCog(bot))

class testCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx):
        await ctx.send("test")


