#creamos una funcion para leer los guildIDs de un archivo.txt, almacenandolos en una lista
def read_guilds():
    with open("./HelpingHandBot/guilds.txt", "r") as f:
        servers = f.read().splitlines()
        servers = [int(x) for x in servers]
        return servers

#leer access.txt para obtener el link de acceso a la base de datos
def read_access():
    with open("access.txt", "r") as f:
        return f.read()


"""creamos una funcion que obtiene el token del bot desde token.txt"""
def read_token():
    with open("token.txt", "r") as f:
        return f.read()
