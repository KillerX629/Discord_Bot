from discord.commands.commands import Option, slash_command
import pymongo
import discord
from discord.ext import commands
from discord import option
import sys

sys.path.append('HelpingHandBot')

from auxFunctions import *



testServers = read_guilds()


def setup(bot):
    bot.add_cog(DBCog(bot))




class DBCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cluster = pymongo.MongoClient(read_access())
        

    @commands.slash_command(guild_ids=testServers, name="testaddmoney")
    @commands.is_owner()
    async def testaddmoney(self, ctx, 
                           usuario:Option(discord.Member,'El usuario a quien se le añadirá'),
                           cantidad:Option(int,'La cantidad de dinero a añadir')):
        
        
        if self.cluster.get_database(name=str(ctx.guild.id)).get_collection("users").find_one({"_id":usuario.id}) is None:
            self.cluster.get_database(name=str(ctx.guild.id)).get_collection(
                "users").insert_one({"_id": usuario.id, "money": cantidad})
        else:
            self.cluster.get_database(name=str(ctx.guild.id)).get_collection(
                "users").update_one({"_id": usuario.id}, {"$inc": {"money": cantidad}})
            
        await ctx.respond("Se ha añadido " + str(cantidad) + " monedas a " + usuario.name)

    @commands.slash_command(guild_ids=testServers, name="createWork")
    async def createWork(self, ctx,
                         nombre:Option(str,'El nombre del trabajo'),
                         paga:Option(int,'La paga del trabajo'),
                         descripcion:Option(str,'La descripción del trabajo'),
                         tiempo:Option(int,'El tiempo que tarda en completarse el trabajo en minutos'),
                         produce:Option(str,'El producto que produce el trabajo')):
        
        if self.cluster.get_database(name=str(ctx.guild.id)).get_collection("works").find_one({"_id":nombre}) is None:#falta checkear si el item que produce existe
            self.cluster.get_database(name=str(ctx.guild.id)).get_collection(
                "works").insert_one({"_id": nombre, "paga": paga, "descripcion": descripcion, "tiempo": tiempo, "produce": produce})
        else:
            await ctx.respond("Ya existe un trabajo con ese nombre")