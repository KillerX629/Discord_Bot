from discord.ext import commands


class MLCog(commands.Cog):
    def  __init__(self, bot):
        self.bot = bot
    
    def derivative(self,func):#returns the derivative of a function
        func = func.replace('x', '*x')
        func = func.replace('^', '**')
        
    
    
    @commands.slash_command()
    async def derivative(self, ctx, *, equation: str):
        """
        Finds the derivative of an equation.
        """
        await ctx.send(f"The derivative of {equation} is {derivative(equation)}")
    
def setup(bot):
    bot.add_cog(MLCog(bot))