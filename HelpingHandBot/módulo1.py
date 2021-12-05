#Discord Bot (HelpingHand)

import discord
from discord.ext import commands, tasks
import os
import pymongo
import itertools

import asyncio




###################################
#AUXULIARY FUNCTIONS###############

async def addrole(ctx, role):
	member = ctx.message.author
	#newrole = discord.utils.get(ctx.guild.roles, id=str(role['rol_trabajo']))
	await member.add_roles(discord.utils.get(ctx.guild.roles, name=role))

	
"""create a function that reads the token from a file"""
def read_token():
    with open("token.txt", "r") as f:
        return f.read()





################################
#MONGO CLIENT

"""crea una funcion que lea el archivo access.txt y devuelva el string de acceso"""
def get_access():
	with open('access.txt') as f:
		return f.read()


cluster = pymongo.MongoClient(get_access())


mydb = cluster["mydb"]
money = mydb["user_money"]          # modelo de datos: {'_id' : username , 'balance' : cur_balance}
items = mydb["items"]				# modelo de datos: {'_id' : nombre_item , 'value' : valor_item}
inventory = mydb["user_inventory"]  # modelo de datos: {'_id' : username, 'inventory' : {dict->}}{'nombre_item' : cantidad del item}
works = mydb["works"]               # modelo de datos : {'_id' : nombre_trabajo , 'saldo_hora' : saldo_hora , 'rol_trabajo' : rol_trabajo, 'jornada' : jornada}
worker = mydb["worker"]             # modelo de datos: {'_id' : username , 'trabajo' : trabajo , 'jornada_restante' : jornada_restante , 'permitido_empleador' : bool}
settings = mydb["settings"]			# modelo de datos: {'_id'  : guild.id , 'transaction channel' : guild.channel , 'work_interval' : hhmmss}

###############################
#BOT LOGIC#####################


#client = discord.Client()
bot = commands.Bot(command_prefix= ':')
@bot.remove_command('help')


@bot.event
async def on_ready():
	print(f'{bot.user}has connected to Discord!')
#	worktask.start()




@bot.command(pass_context = True,aliases=['alabe','olink'])
async def alabar(ctx):
	await ctx.send(f'ALABADO SEA JUESE BEEP BOOP')


@bot.command()
async def puto(ctx):
	await ctx.send(f'T0DoS PU7O5')



@bot.command()
async def mata(ctx, nombre):
	await ctx.send(f'pium pium! MUERE {nombre}! >:(')


@bot.command()
async def roles(ctx):
	roles = await ctx.guild.fetch_roles()
	await ctx.send(f'los roles del servidor son: {roles} ')# en un f string, se usan los {} para decir que es una variable



@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    await ctx.bot.logout()


##################################################
#  MODULE: SERVER_SETTINGS########################

@bot.command()
async def set_transaction_channel(ctx, channel):
	canal = await commands.TextChannelConverter().convert(ctx , channel)
	update_transaction_channel(ctx, canal)
	await canal.send(f'Se ha establecido a este como el canal donde anunciar las transacciones y pagos')
	
	#await canal.send('test')para mandar un mensaje a un canal especifico
	


##################################################
#BOT MODULE: WORK#################################

@bot.command()
async def create_work(ctx, nombre_trabajo, saldo_hora, rol_trabajo, jornada, produce=None, cantidadp=0, consume=None, cantidadc=0):
	float(saldo_hora)
	float(jornada)
	roles = await ctx.guild.fetch_roles()
	role = await commands.RoleConverter().convert(ctx , rol_trabajo)
	if not nombre_trabajo:
		await ctx.send(f'El nombre del trabajo es invalido')
		return ;
	if isinstance(saldo_hora,float) :
		abs(saldo_hora)
		await ctx.send(f'El saldo por hora ingresado no es un numero')
		return ;
	role_check = discord.utils.get(ctx.guild.roles, name=str(role)) #ESTO SIRVE, TRANSFORMAR EL ROLE EN STRING PARA BUSCARLO
	if role_check is None:
		await ctx.send(f'el rol {role} no existe')
		return ;
	await ctx.send(f'{role} existe')
	if isinstance(jornada,float) :  # noqa: E203, E231, E272
		abs(jornada)
		await ctx.send(f'La jornada laboral no tiene un numero como valor')
		return ;

	if ctx.author.guild_permissions.administrator:
		await ctx.send(f'pagar� el gobierno el trabajo? \nS:si N:no \nen caso de no, usted pagar� el sueldo')
		msg = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
		if msg.content==('s' or 'S'):
			dueño = "gov't"
		else:
			dueño=ctx.author.id

	if(produce is not None):
		item = items.find_one({'_id' : produce})
		if item is None:
			await ctx.send(f'el �tem especificado no existe, el trabajo no producir� nada')
			produce = None
	if cantidadp <= 0:
		cantidadp = 0
	if(consume is not None):
		item = items.find_one({'_id':consume})
		if item is None:
			await ctx.send(f'el �tem especificado no existe, el trabajo no consumir� nada')
			consume = None
	if cantidadc <= 0:
		cantidadc = 1

	check = upload_new_work(nombre_trabajo,saldo_hora,role.name,jornada,dueño,produce)
	if  check == False:
		await ctx.send(f'Ya hab�a un trabajo con el nombre especificado')
	else:
		await ctx.send(f'se ha creado el trabajo exitosamente!')



@bot.command()
async def get_works(ctx):
	trabajos = list(works.find({}))
	await ctx.send(f'{trabajos}')


@bot.command()
async def work(ctx, workID):
	trabajo = find_work(workID)
	await ctx.send(f'{trabajo}')
	if trabajo == None:
		await ctx.send(f'El trabajo especificado no existe en la base de datos')
		return ;
	item =  worker.find_one({'_id' : ctx.author.id})
	#next((item for item in works if item['_id']==ctx.author.id),None)
	await ctx.send(f'{item}')
	if item is None:
		await ctx.send(f'Como es su primera vez trabajando, deber� autorizarlo el empleador:')
		if trabajo['due�o'] is not "gov't":
			await ctx.send(f'{(await discord.ext.commands.MemberConverter().convert(ctx, str(trabajo.get("due�o")))).mention} por favor autorice al nuevo trabajador (este proceso ocurre solo la primera vez)\nPara autorizar, conteste con "s" o "S"')
			msg = await bot.wait_for('message', check=lambda message: message.author.id == trabajo.get("due�o"))
		if  trabajo['due�o'] == "gov't":
			await ctx.send(f'Usted ha sido autorizado')
			post = {'_id' : ctx.author.id , 'trabajo' : trabajo['_id'] , 'jornada_restante' : trabajo['jornada'] , 'permitido_empleador' : True}
			add_worker(post)
		elif msg.content == ('s' or 'S'):
			await ctx.send(f'Usted ha sido autorizado')
			post = {'_id' : ctx.author.id , 'trabajo' : trabajo['_id'] , 'jornada_restante' : trabajo['jornada'] , 'permitido_empleador' : True}
			add_worker(post)
	else:
		if item.get('permitido_empleador') and item['_id'] == workID and item['jornada_restante']==0:
			item['jornada_restante']=trabajo.jornada
			item.trabajo = trabajo._id
			update_worker(ctx, item)
		if item['_id'] is not trabajo['_id']:
			if int(item['jornada_restante'])>0:
				await ctx.send(f'No puede cambiar de trabajo mientras esta en otro empleo')
				return 
			else:
				item.trabajo = trabajo['_id']
				item.jornada_restante = trabajo.jornada
				item.permitido_empleador = False
				await ctx.send(f'Como est� cambiando de trabajo, deber� pedirle permiso a su nuevo empleador:')
				if trabajo['due�o'] != "gov't":
					#await ctx.send(f'{discord.utils.get(ctx.guild.members , id= trabajo.get("due�o"))} por favor autorice al nuevo trabajador (este proceso ocurre solo la primera vez)\nPara autorizar, conteste con "s" o "S"')
					await ctx.send(f'{(await discord.ext.commands.MemberConverter().convert(ctx, str(trabajo.get("due�o")))).mention} por favor autorice al nuevo trabajador (este proceso ocurre solo la primera vez)\nPara autorizar, conteste con "s" o "S"')
					msg = await bot.wait_for('message', check=lambda message: message.author.id == trabajo.dueño)
				if trabajo.get("due�o") == "gov't":
					await ctx.send(f'Usted ha sido autorizado')
					item.permitido_empleador=True
					update_worker(ctx, item)
				elif  msg.content == ('s' or 'S'):
					await ctx.send(f'Usted ha sido autorizado')
					item.permitido_empleador=True
		if item.trabajo == trabajo._id and item.permitido_empleador == True:
			item.jornada_restante = trabajo.jornada
			update_worker(ctx, item)


@bot.command()
async def stop_working(ctx):
	if(stop_worker(ctx.author.id)):
		await ctx.send(f'usted ha dejado de trabajar')
	else:
		await ctx.send(f'usted no est� trabajando')

@bot.command()
async def get_worker(ctx, username=None):
	if username is None:
		await ctx.send(f'{get_worker(ctx.author.id)}')
	else :
		await ctx.send(f'{get_worker(username)}')

######################################################
# BOT MODULE : MONEY##################################

@bot.command()
async def pay(ctx, user, ammount):
	usuario = commands.UserConverter().convert(ctx, user)
	if discord.utils.get(ctx.guild.members, usuario) is None:
		await ctx.send(f'No se encontr� al usuario especificado')
	else:
		if db_pay(ctx.author.id, abs(ammount), usuario ):
			await ctx.send(f'se ha realizado el pago con �xito')
			return
		else:
			await ctx.send(f'no se ha podido realizar el pago')
			return


########################################
#MODULE_INVENTORY#######################

@bot.command()
async def create_item(ctx, name, value:float=0 ):
	if not name:
		await ctx.send(f'Debe ingresar un nombre valido')
		return ;

	if  isinstance(value, float):
		check = new_item(name, value)
		if check:
			await ctx.send(f'Se ha creado el nuevo objeto de forma satisfactoria!')
		elif not check:
			await ctx.send(f'No se ha podido crear el objeto (ya existe un objeto con ese nombre)')

@bot.command()
async def add_item(ctx, name, quantity, user=None):
	usuario = discord.utils.get(ctx.guild.members, user)
	if isinstance(quantity, int) :
		if quantity > 0:
			if name:
				if user == None:
					add_item_db(ctx.author.id, name, quantity)
				elif  usuario is not None:
					add_item_db(usuario.id, name, quantity)

@bot.command()
async def edit_work(ctx):
	trabajos = list(works.find({}))
	await ctx.send(f'Los trabajos existentes son los siguientes:\n{trabajos}')
	await ctx.send(f'escriba el nombre del trabajo que desea editar:')
	msg = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
	next((item for item in trabajos if item._id == msg.content), None)
	if item is None:
		await ctx.send(f'el trabajo nombrado no existe')
		return ;
	await ctx.send(f'escriba el atributo que quiere cambiar')
	msg2 = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
	if msg2.content == 'saldo_hora':
		await ctx.send(f'de un nuevo salario para el trabajo')
		msg = await bot.wait_for('message',check=lambda message: message.author == ctx.author)##########TERMINAR ESTA FUNCIOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOON

#########################################
# WORK TASK##############################

#@tasks.loop(seconds = 15)
#async def worktask():
#	trabajadores = list(worker.find({'jornada_restante':{'$gt': 1}}))
#	trabajos = list(works.find({}))
#	for guild in bot.guilds:
#		config = settings.find_one({'_id' : guild.id})
#		print (f'{guild.id}')
#		if config is None:
#			continue
#		canal = config.get('transaction_channel')
#		#a�adir linea para leer config de pasaje de tiempo
#		if canal != 0:
#			channel = bot.get_channel(canal)
#		else :
#			channel = None
#		for trabajador in trabajadores:
#			#trabajo = next(work for work in trabajos if work.get('nombre_trabajo')==trabajador.get('trabajo'))
#			for trabajo in trabajos:# NECESITO EL TRABAJO EN ESPECIFICOOOO
#				clear = True
#				if trabajo.get('consume') is not None:
#					clear = remove_item(trabajo['due�o'], trabajo['consume'] , trabajo['cantidadc'])
#				if db_pay(trabajo.get('due�o'), trabajo.get('saldo_hora'), trabajador.get('_id')) and clear:
#					trabajador['jornada_restante']-=1
#					if channel is not 0:  
#						channel.send(f"{discord.utils.get(guild.members,id = trabajo['due�o']).nick} ha pagado a {discord.utils.get(guild.members,id = trabajador['_id']).nick} su jornada laboral")
#				else:
#					trabajador['jornada_restante']=0
#					if channel is not 0:
#						if trabajo['due�o'] is "gov't":
#							channel.send(f'El gobierno no ha podido pagarle a {discord.utils.get(guild.members, id=trabajador["_id"]).mention} su jornada!')
#						else:
#							channel.send(f'{discord.utils.get(guild.members, id = trabajo["due�o"]).mention} no ha podido pagar a {discord.utils.get(guild.members,id=trabajador["_id"]).mention} su jornada!')
#						if not clear:
#							if trabajo['due�o'] is not "gov't":
#								channel.send(f' {discord.utils.get(guild.members, id= trabajo["due�o"]).mention} no tiene los materiales suficientes para realizar el trabajo {trabajo["_id"]}')
#							else:
#								channel.send(f'El gobierno no tiene los materiales necesarios para realizar el trabajo')
#				if trabajador['jornada_restante'] << 1:
#					if channel is not 0:
#						channel.send(f'{discord.utils.get(guild.members, id= trabajador["_id"]).mention} vuelve a su casa despu�s de un duro dia de trabajo')
#				if trabajo['produce'] is not None:
#					add_item_db(trabajo['due�o'], trabajo['produce'] , trabajo['cantp'])


#modelo de datos : {'_id' : nombre_trabajo , 'saldo_hora' : saldo_hora , 'rol_trabajo' : rol_trabajo, 'jornada' : jornada}
#modelo de datos: {'_id' : username , 'trabajo' : trabajo , 'jornada_restante' : jornada_restante , 'permitido_empleador' : bool}	


#########################################
#BOT_HELP################################

@bot.command()
async def help(ctx):
	embed = discord.Embed()
		

	embed.set_author(name='Help')
	embed.add_field(name="alabar", value='alaba')
	embed.add_field(name='create_work', value='crea un trabajo, los datos se envian de la siguiente forma: "nombre del trabajo" saldo_hora rol_asignado jornada_laboral "material que produce"')
	embed.add_field(name= "get_works", value='retorna todos los trabajos disponibles en la base de datos')
	embed.add_field(name="get_worker", value='{nombre de usuario=None} devuelve el estado de trabajo actual del usuario (o de no haber usuario, del que use el comando)')
	embed.add_field(name='create_item', value='{"nombre del item" valor_del_item} crea un item nuevo en la base de datos, dandole nombre y precio por unidad al mismo')
	embed.add_field(name='work', value='"nombre del trabajo" el usuario intentar� trabajar con el trabajo especificado, de ser su primera vez, su jefe (si hay uno) deber� autorizarlo')
	embed.add_field(name="add_item", value='"nombre del item" cantidad @usuario=None   le a�ade al inventario del usuario especificado (o del autor de no haber ninguno) el item especificado en la cantidad especificada')

########################################
#DATABASE INTERACTIONS##################

def find_work(workID):
	trabajo = works.find_one({"_id" : workID})
	print(trabajo)
	if trabajo is None:
		return False
	else:
		return  trabajo



def add_money(user,quantity):
	cuenta = money.find_one({'_id' : user})
	abs(quantity)
	if cuenta == None:
		post = {'_id' : user, 'balance': quantity}
		money.insert_one(post)
	else:
		cuenta.balance+= quantity
		money.update_one({'_id':user}, cuenta)

def update_transaction_channel(ctx, channel):
	post = {'transaction channel' : channel.id}
	setting = settings.find_one({'_id' : ctx.guild.id})
	if setting is None:
		settings.insert_one({'_id' : ctx.guild.id , 'transaction_channel' : channel.id})
	else:
		settings.update_one({'_id' : ctx.guild.id}, {'transaction_channel' : channel.id})




async def  add_item_db( user, name , quantity):  # noqa: F811
	inventario = list(inventory.find({"_id" : name}))
	if (inventario == None):
		post = {"_id" : user, 'inventory' : {name : quantity}}
		inventory.insert_one(post)
		return True
	else:
		if name not in inventario['inventory']:
			item = items.find_one({'_id' : name})
			if item is not None:
				inventario['inventory']['name'] = quantity
				inventory.update({'_id' : name} ,inventario)
				return True
			if item is None:
				return False
		if name in inventario['inventory']:
			inventario['inventory']['name']+=quantity
			inventory.update_one({'_id': name}, inventario)
			return True


async def  remove_item(user, name , quantity):
	inventario = list(inventory.find({"_id" : name}))
	if (inventario == None):
		return False
	else:
		if name not in inventario['inventory']:
			return False
		if name in inventario['inventory']:
			if inventario['inventory']['name'] << quantity:
				return False
		inventario['inventory']['name']-=quantity
		inventory.update_one({'_id' : user}, inventario)





def stop_worker(id):

	trabajador = worker.find({'_id':id})
	if trabajador:
		worker.update_one({'_id':id},{'jornada_restante': 0})
		return True
	else:
		return False

def db_pay(userPay, amount, userRecieve):
	if userPay == "gov't":
		pay = None
	else:
		pay = money.find_one({'_id' : userPay})
	recieve = money.find_one({'_id' : userRecieve})
	if recieve == None:
		money.insert_one({'_id' : userRecieve , 'balance' : 0})
		recieve = money.find_one({'_id' : userRecieve})
	if pay is not None:
		if pay.balance << amount :
			return False
		pay.balance -= amount
		recieve['balance'] += amount
		money.update_one({'_id' : pay.get('_id')}, pay)
		money.update_one({'_id' : recieve.get('_id')}, recieve)
		return True
	else:
		recieve['balance'] += amount
		money.update_one({'_id' : recieve.get('_id')}, {'$set' :{'balance': recieve['balance']}})

def add_worker(post):
	try:
		worker.insert_one(post)
		return True
	except pymongo.errors.DuplicateKeyError:
		return False

def update_worker(ctx, post):
	worker.update_one({'_id' : post._id}, post)
	return True

def get_worker(username):
	return worker.find_one({'_id' : username})


def new_item(name, value):
	post = {"_id" : name , "value" : value}
	try:
		items.insert_one(post)
		return True
	except pymongo.errors.DuplicateOptionError:
		return False



def upload_new_work(nombre_trabajo, saldo_hora: float, rol_trabajo, jornada: float, dueño, produce):
	post = {"_id" : nombre_trabajo , "saldo_hora" : saldo_hora , "rol_trabajo" : rol_trabajo , "jornada" : jornada , "due�o" : dueño , 'produce' : produce}
	try:
		works.insert_one(post)
		return True
	except pymongo.errors.DuplicateKeyError:
		return False













#####################################################
#BOT: RUN###########ESTO NO SE TOCA #################
bot.run(read_token())
