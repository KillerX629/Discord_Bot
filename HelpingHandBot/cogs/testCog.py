from discord.ext import commands

class testCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx):
        await ctx.respond("test")

    def cog_load(self):
        print("testCog loaded")