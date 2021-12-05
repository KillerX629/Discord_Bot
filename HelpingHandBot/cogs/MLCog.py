from discord.ext import commands

class perceptron():
    def __init__(self, input_size):
        self.weights = [0 for _ in range(input_size)]
        self.bias = 0
        self.learning_rate = 0.1

    def train(self, inputs, expected_output):
        output = self.predict(inputs)
        error = expected_output - output
        self.weights = [w + self.learning_rate * error * i for i, w in zip(inputs, self.weights)]
        self.bias = self.bias + self.learning_rate * error

    def predict(self, inputs):
        return self.bias + sum(i * w for i, w in zip(inputs, self.weights))

    
class layer():
    def __init__(self, input_size, output_size):
        self.perceptrons = [perceptron(input_size) for _ in range(output_size)]

    def train(self, inputs, expected_output):
        for perceptron in self.perceptrons:
            perceptron.train(inputs, expected_output)

    def predict(self, inputs):
        return [perceptron.predict(inputs) for perceptron in self.perceptrons]

class model():
    def __init__(self, input_size, hidden_size, output_size):
        self.layers = [layer(input_size, hidden_size), layer(hidden_size, output_size)]

    def train(self, inputs, expected_output):
        for layer in self.layers:
            layer.train(inputs, expected_output)
            inputs = layer.predict(inputs)

    def predict(self, inputs):
        for layer in self.layers:
            inputs = layer.predict(inputs)
        return inputs


class MLCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.model=model(1,2,1)

    #creamos un comando que, una vez invocado,
    #el bot leerá los ultimos 100 mensajes del canal donde se invocó
    #e intentará generar un mensaje mediante una red neuronal
    @commands.slash_command()
    async def ml(self, ctx):
        #obtenemos los ultimos 100 mensajes del canal donde se invocó
        messages = await ctx.channel.history(limit=100).flatten()
        #obtenemos los mensajes en formato de texto
        messages = [m.content for m in messages]
        #obtenemos el mensaje de entrada
        input_message = messages[-1]
        #obtenemos el mensaje de salida
        output_message = messages[-2]
        #creamos una lista con los mensajes de entrada
        input_list = [input_message]
        #creamos una lista con los mensajes de salida
        output_list = [output_message]
        #entrenamos el modelo con los mensajes de entrada y salida
        self.model.train(input_list, output_list)
        #creamos una lista con el mensaje de entrada
        input_list = [input_message]
        #predecimos el mensaje de salida
        output_list = self.model.predict(input_list)
        #obtenemos el mensaje de salida
        output_message = output_list[0]
        #enviamos el mensaje de salida
        await ctx.send(output_message)

    
def setup(bot):
    bot.add_cog(MLCog(bot))