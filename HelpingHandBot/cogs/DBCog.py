from discord.commands.commands import Option, slash_command
import pymongo
import discord
from discord.ext import commands
from discord import option
import os
import sys

current = os.path.dirname(os.path.realpath(__file__))

parent = os.path.dirname(current)

sys.path.append(parent)


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
        print(read_access())
        
        if self.cluster.get_database(name=str(ctx.guild.id)).get_collection("users").find_one({"_id":usuario.id}) is None:
            self.cluster.get_database(name=str(ctx.guild.id)).get_collection(
                "users").insert_one({"_id": usuario.id, "money": cantidad})
        else:
            self.cluster.get_database(name=str(ctx.guild.id)).get_collection(
                "users").update_one({"_id": usuario.id}, {"$inc": {"money": cantidad}})

