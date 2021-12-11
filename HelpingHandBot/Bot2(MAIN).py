from typing_extensions import Required
import discord 
from discord.ext import commands
from discord import Option
import random
import pymongo #depende también de DNSPython
import os
from auxFunctions import *


intents = discord.Intents.default()
intents.members = True



bot = commands.Bot(command_prefix="?", intents=intents)








    
db = pymongo.MongoClient(read_access())




#los cogs sirven para dividir el codigo en partes, dentro de un cog se pueden poner comandos y eventos
#importamos los cogs que esten en la carpeta ./cogs
#para cargarse, un cog necesita la funcion Setup
for filename in os.listdir('./HelpingHandBot/cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')
    else:
        print("No se ha podido cargar el cog: " + filename[:-3])



"""
ctx.send was an alias to ctx.respond in the alpha, however this was changed in the slash branch and will remain like this.
 ctx.send now just sends a message to the channel, 
you need to respond at least once to not get the This interaction failed!
"""




token = read_token()


testServers=read_guilds()


#744519581598744669,654478468540792845

"""create an event that, given a command execution in a server, checks if the bot has permissions to do so"""
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send("You do not have permission to use this command!")
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send("You are missing a required argument!")
    elif isinstance(error, commands.errors.BadArgument):
        await ctx.send("Bad argument!")
    elif isinstance(error, commands.errors.CommandNotFound):
        await ctx.send("Command not found!")
    elif isinstance(error, commands.errors.CommandOnCooldown):
        await ctx.send("Command on cooldown!")
    elif isinstance(error, commands.errors.DisabledCommand):
        await ctx.send("Command disabled!")
    elif isinstance(error, commands.errors.TooManyArguments):
        await ctx.send("Too many arguments!")
    elif isinstance(error, commands.errors.UserInputError):
        await ctx.send("User input error!")
    elif isinstance(error, commands.errors.CommandInvokeError):
        await ctx.send("Command invoke error!")
    elif isinstance(error, commands.errors.CommandError):
        await ctx.send("Command error!")
    elif isinstance(error, commands.errors.MissingPermissions):
        await ctx.send("Missing permissions!")
    elif isinstance(error, commands.errors.BotMissingPermissions):
        await ctx.send("Bot missing permissions!")


@bot.slash_command(guild_ids=testServers, name="test", aliases=["test"], description="test", usage="test")
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")

@bot.slash_command(guild_ids=testServers)
async def hello(ctx,
    causa:Option(str,'lo que queres que se diga a el usuario'),
    usuario: Option(discord.Member,'el usuario al que quieres que se lo diga',required=False,default=None)):
    await ctx.defer()
    if usuario is None:
        usuario = ctx.author
    await ctx.respond(f"Hola {usuario.mention}! {causa}")


@bot.user_command(guild_ids=testServers)
@commands.is_owner()
async def jeringoso(ctx,user:discord.Member):
    respuesta = ""
    for i in range(len(user.name)):
        match user.name[i]:
            case 'a':
                respuesta += 'apa'
            case 'e':
                respuesta += 'epe'
            case 'i':
                respuesta += 'ipi'
            case 'o':
                respuesta += 'opo'
            case 'u':
                respuesta += 'upu'
            case default:
                respuesta += user.name[i]
    
    await ctx.respond(f"El nombre de {user.mention} en jeringoso es: {respuesta}")
                


@bot.user_command(guild_ids=testServers, name='Puto')
async def puto(ctx, user: discord.Member):
    await ctx.defer()
    await ctx.respond(f"{user.mention} es un puto")

@bot.message_command(guild_ids=testServers, name='mensajefuncion')
async def mensajefuncion(ctx, mensaje: discord.Message):
    await ctx.defer()
    await ctx.respond(f"{ctx.author} pidió que se reenviara lo siguiente:\n\"{mensaje.content}\"")


"""create a slash command that shows the users inside the current guild"""
@bot.slash_command(guild_ids=testServers, name='users')
async def users(ctx):
    await ctx.defer()
    await ctx.send(f"{ctx.guild.name} has {len(ctx.guild.members)} members")
    await ctx.send(f"los miembros del servidor son:")
    for member in ctx.guild.members:
        await ctx.respond(f"{member.name}")
    

@bot.slash_command(guild_ids=testServers, name='stop')
@commands.is_owner()
async def STOP(ctx):
    #el comando stop hace que el bot frene su ejecución inmediatamente
    await ctx.respond(":thumbsup:")
    await bot.close()
    


"""create a slash command that mentions 3 users at random from the guild"""
@bot.slash_command(guild_ids=testServers, name='randomchoiceguild')
async def randomchoiceguild(ctx):
    users = ctx.guild.members
    await ctx.respond(f"{random.choice(users).mention}, {random.choice(users).mention}, {random.choice(users).mention}")
    

@bot.event
async def on_command_error(ctx, exc):
    etype = type(exc)
    trace = exc.__traceback__
    verbosity = 4
    lines = traceback.format_exception(etype, exc, trace, verbosity)

    traceback_text = ''.join(lines)
    await ctx.channel.send(traceback_text)




bot.run(token)