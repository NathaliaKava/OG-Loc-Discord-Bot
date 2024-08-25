from typing import Final
import discord
import os
import random
from dotenv import load_dotenv
from discord import Intents, Client, Message
from discord.ext import commands
from random import choice, randint
from discord import FFmpegPCMAudio


load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')


intents: Intents = Intents.default()
intents.message_content = True
intents.voice_states = True
client = commands.Bot(command_prefix='!', intents=intents)


async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('(Message estava vazio porque as intenções provavelmente não foram habilitadas)')
        return

    is_private = user_message[0] == '?'
    if is_private:
        user_message = user_message[1:]

    try:
        response: str = get_response(user_message)

        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)


def get_response(user_input: str) -> str:
    if user_input.startswith('!'):
        return ''
    else:
        lowered: str = user_input.lower()

        if lowered == '':
            return 'Bem, você está demasiado silencioso...'
        elif 'olá' in lowered:
            return 'Olá!'
        elif 'como você está?' in lowered:
            return 'bem, obrigado!'
        elif 'tchaw' in lowered:
            return 'Até breve!'
        elif 'lançar dados' in lowered:
            return f'Você obteve: {randint(1, 6)}'
        else:
            return choice(['Eu não entendi...',
                           'O que você disse?',
                           'Você se importa em reformular isso?'
                           'Filho da puta, vou caçar sua mãe'])


@client.event
async def on_ready() -> None:
    print(f'{client.user} está online!')


@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f'[{channel}] {username}: "{user_message}"')
    await send_message(message, user_message)
    await client.process_commands(message)


@client.command(name='join')
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.message.author.voice.channel
        voice = await channel.connect()

        diretorio = os.path.dirname(os.path.abspath(__file__))
        arquivos_de_musica = [f for f in os.listdir(diretorio) if f.endswith('.mp3')]
        musica_aleatoria = random.choice(arquivos_de_musica)

        source = FFmpegPCMAudio(os.path.join(diretorio, musica_aleatoria))
        player = voice.play(source)
        print(f"Tocando: {musica_aleatoria}")

    else:
        await ctx.send("Você precisa estar em um canal de voz para usar este comando")


@client.command(name='leave')
async def leave(ctx):
    voice_client = ctx.voice_client
    if voice_client:
        await voice_client.disconnect()
        await ctx.send('OG Loc saiu do canal de voz.')
    else:
        await ctx.send('OG Loc não está em um canal de voz.')


@client.command(name='pause')
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send('Não há músicas tocando no momento.')


@client.command(name='resume')
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send('Nenhuma música está pausada!')


@client.command(name='stop')
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()


client.run(TOKEN)