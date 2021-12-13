import re
from typing_extensions import Required
from discord.commands.commands import Option, slash_command
from discord.ext.commands.core import T, check
import pymongo
import discord
from discord.ext import commands
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
                           cantidad:Option(int,'La cantidad de dinero a añadir',default=0)):
        
        
        if self.cluster.get_database(name=str(ctx.guild.id)).get_collection("users").find_one({"_id":usuario.id}) is None:
            self.cluster.get_database(name=str(ctx.guild.id)).get_collection(
                "users").insert_one({"_id": usuario.id, "money": cantidad})
        else:
            self.cluster.get_database(name=str(ctx.guild.id)).get_collection(
                "users").update_one({"_id": usuario.id}, {"$inc": {"money": cantidad}})
            
        await ctx.respond("Se ha añadido " + str(cantidad) + " monedas a " + usuario.name)

    @commands.slash_command(guild_ids=testServers, name="creatework")
    async def createWork(self, ctx,
                         nombre:Option(str,'El nombre del trabajo',Required=True),
                         paga:Option(int,'La paga del trabajo',min=1),
                         descripcion:Option(str,'La descripción del trabajo'),
                         tiempo:Option(int,'El tiempo que tarda en completarse el trabajo en minutos'),
                         produce:Option(str,'El producto que produce el trabajo')):
        
        if self.cluster.get_database(name=str(ctx.guild.id)).get_collection("works").find_one({"_id":nombre}) is None:
            if self.cluster.get_database(name=str(ctx.guild.id)).get_collection("items").find_one({"_id":produce}) is None:
                await ctx.respond("El item que produce no existe, se creará un trabajo que no produce items")
                self.cluster.get_database(name=str(ctx.guild.id)).get_collection("works").insert_one(
                    {"_id": nombre, "paga": paga, "descripcion": descripcion, "tiempo": tiempo, "produce": None})
            else:
                self.cluster.get_database(name=str(ctx.guild.id)).get_collection(
                    "works").insert_one({"_id": nombre, "paga": paga, "descripcion": descripcion, "tiempo": tiempo, "produce": produce, "dueño": ctx.author.id})
            
        else:
            await ctx.respond("Ya existe un trabajo con ese nombre")
        
    @commands.slash_command(guild_ids=testServers, name="showserveritems")
    async def showServerItems(self, ctx):
        baseDeDatos = self.cluster.get_database(name=str(ctx.guild.id))
        cluster = baseDeDatos.get_collection("items")
        items = cluster.find()
        #damos formato al texto resultante para que sea más legible:
        await ctx.respond("```" + "\n".join(["{}:{}, {}$".format(item["_id"],item["descripcion"],item["precio"]) for item in items]) + "```")
    
    @commands.slash_command(guild_ids=testServers, name="showuseritems")
    async def showuseritems(self,ctx):
       await ctx.respond(str(self.cluster.get_database(name=str(ctx.guild.id)).get_collection("users").find_one({"_id":ctx.author.id}.get("items"))))
            
    @commands.slash_command(guild_ids=testServers, name="spawnitem")
    @commands.is_owner()
    async def spawnItem(self,ctx,
                       item:Option(str,'El item que se dara',Required=True),
                       quantity:Option(int,'La cantidad de items que se daran',min=1),
                       user:Option(discord.Member,'El usuario al que se le dará el item',Required=False,default=None)):
        
        if self.getItem(item):
            await self.giveitem(item, ctx.author.id if user is None else user ,quantity)
            await ctx.respond("Se han añadido " + str(quantity) + " " + item + " al inventario de " + ctx.author.name if user is None else user.name)
        else:
            await ctx.respond("El item no existe")
    
    @commands.slash_command(guild_ids=testServers, name="createitem")
    @commands.is_owner()
    async def createItem(self, ctx,
                         name:Option(str,'El nombre del item',Required=True),
                         desc:Option(str,'La descripción del item'),
                         price:Option(float,'El precio del item'),
                         type:Option(str,'El tipo de item')):
        if self.cluster.get_database(name=str(ctx.guild.id)).get_collection("items").find_one({"_id":name}) is None:
            self.cluster.get_database(name=str(ctx.guild.id)).get_collection(
                "items").insert_one({"_id": name, "descripcion": desc, "precio": price, "tipo": type})
            await ctx.respond("Se ha creado el item " + name)
        else:
            await ctx.respond("Ya existe un item con ese nombre")
            
      
    @commands.slash_command(guild_ids=testServers, name="checkservers")
    @commands.is_owner()
    async def checkservers(self, ctx):
        #observando en todos los servidores en los cuales es miembro el bot, enviamos:
        #guild_id: guild_id
        #guild_name: guild_name
        #Existe la base de datos: True/False
        await ctx.respond("Lista de servidores en los que estoy:")
        for guild in self.bot.guilds:
            await ctx.respond("guild_id: " + str(guild.id) + " guild_name: " + guild.name + " Existe la base de datos: " + str (await self.check_if_svDB_exists(guild.id)))
          
    #funciones auxiliares para interactuar con la base de datos
    
    async def check_if_svDB_exists(self,guild_id:int):
        basesDeDatos = self.cluster.list_database_names()
        if str(guild_id) in basesDeDatos:
            return "True"
        else:
            return "False"
        
    async def giveitem(self,item:str,user:discord.Member,quantity:int):
        baseDeDatos = self.cluster.get_database(name=str(user.guild.id))
        cluster = baseDeDatos.get_collection("users")
        if cluster.find_one({"_id":user.id}) is None:
            cluster.insert_one({"_id":user.id,"items":{item:quantity}})
        else:
            cluster.update_one({"_id":user.id},{"$inc":{"items."+item:quantity}})
            
    async def getItemCountUser(self,item:str,user:discord.Member):
        baseDeDatos = self.cluster.get_database(name=str(user.guild.id))
        cluster = baseDeDatos.get_collection("users")
        if cluster.find_one({"_id":user.id}) is None:
            return 0
        else:
            return cluster.find_one({"_id":user.id})["items"][item]
    
    async def subtractitem(self,item:str,user:discord.Member,quantity:int):
        baseDeDatos = self.cluster.get_database(name=str(user.guild.id))
        cluster = baseDeDatos.get_collection("users")
        if cluster.find_one({"_id":user.id}) is None:
            return False
        else:
            #buscamos si la cantidad actual del item es mayor o igual a la cantidad que queremos restar
            #si no lo es, devolvemos False
            if cluster.find_one({"_id":user.id})["items"][item] >= quantity:
                cluster.update_one({"_id":user.id},{"$inc":{"items."+item:-quantity}})
                return True
            else:
                return False
            
    async def getItem(self,item:str): 
        #observamos si el item existe en la base de datos
        baseDeDatos = self.cluster.get_database(name=str(ctx.guild.id))
        cluster = baseDeDatos.get_collection("items")
        if cluster.find_one({"_id":item}) is None:
            return False
        else:
            return True
        
    
    