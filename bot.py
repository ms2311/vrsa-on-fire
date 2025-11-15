import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Configurar intents (IMPORTANTE!)
intents = discord.Intents.default()
intents.members = True           # necessário para on_member_join
intents.message_content = True   # necessário para ler mensagens

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Bot ligado como {bot.user}")


@bot.event
async def on_member_join(member: discord.Member):
    """
    Quando alguém entra no servidor:
    1. Tenta mandar DM a pedir o nick do Clash
    2. Espera resposta
    3. Muda o nickname no servidor
    """
    try:
        # Tenta enviar DM
        dm_channel = await member.create_dm()
        await dm_channel.send(
            f"👋 Olá {member.name}! Bem-vindo ao servidor!\n"
            "Por favor, envia o teu **nick do Clash** para eu te pôr com esse nome aqui no servidor."
        )

        def check(msg: discord.Message):
            # Garante que é a mesma pessoa e no DM
            return msg.author == member and msg.channel == dm_channel

        # Esperar pela resposta (60 segundos)
        try:
            reply: discord.Message = await bot.wait_for(
                "message",
                timeout=120.0,
                check=check
            )
        except asyncio.TimeoutError:
            await dm_channel.send("⏰ Não recebi resposta a tempo. Tenta outra vez mais tarde se quiseres mudar o nick.")
            return

        clash_nick = reply.content.strip()

        # Tentar mudar o nickname no servidor
        try:
            await member.edit(nick=clash_nick, reason="Definido pelo bot com nick do Clash")
            await dm_channel.send(f"✅ Nickname no servidor definido para **{clash_nick}**!")
        except discord.Forbidden:
            # Sem permissão para mudar o nick
            await dm_channel.send(
                "⚠️ Não consigo mudar o teu nick no servidor (faltam permissões ao bot ou o meu cargo é muito baixo)."
            )
        except Exception as e:
            print(f"Erro ao mudar nickname de {member}: {e}")
            await dm_channel.send("⚠️ Ocorreu um erro ao tentar mudar o teu nick.")

    except discord.Forbidden:
        # DMs bloqueadas
        print(f"Não consegui enviar DM para {member}. DMs bloqueadas.")
    except Exception as e:
        print(f"Erro no on_member_join para {member}: {e}")

bot.run(TOKEN)

