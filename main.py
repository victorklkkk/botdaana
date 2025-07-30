# main.py

import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv  # Importa a função da biblioteca python-dotenv

# --- CARREGAMENTO DAS VARIÁVEIS DE AMBIENTE ---
# Esta função procura por um ficheiro .env na raiz do projeto e carrega as suas variáveis.
load_dotenv()

# --- CONFIGURAÇÃO INICIAL ---

# Define as "intenções" do bot (quais eventos ele pode "ouvir")
intents = discord.Intents.default()
intents.members = True          # Necessário para eventos de membros (como a verificação)
intents.message_content = True  # Necessário para ler o conteúdo de mensagens (comandos)

# Cria a instância do bot com o prefixo '!' e as intents definidas
bot = commands.Bot(command_prefix='!', intents=intents)

# Obtém o token a partir do ambiente.
# A função os.getenv() agora consegue ler o valor carregado do .env
TOKEN = os.getenv('DISCORD_TOKEN')


# --- CARREGAMENTO DOS COGS (MÓDULOS DO BOT) ---

async def load_cogs():
    """Encontra e carrega todos os ficheiros de cog na pasta /cogs."""
    # Percorre todos os ficheiros na pasta 'cogs'
    for filename in os.listdir('./cogs'):
        # Verifica se o ficheiro é um ficheiro Python (.py)
        if filename.endswith('.py'):
            # Carrega o cog. A sintaxe é 'pasta.nome_do_ficheiro' sem o .py
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'✅ Cog carregado: {filename}')
            except Exception as e:
                print(f'❌ Falha ao carregar o cog {filename}: {e}')


# --- EVENTO ON_READY ---
# Este evento é acionado quando o bot está online e totalmente conectado ao Discord.

@bot.event
async def on_ready():
    """Função executada quando o bot está pronto."""
    print('-------------------')
    print(f'Bot conectado como {bot.user}')
    print(f'ID do Bot: {bot.user.id}')
    print('Bot está pronto e funcional!')
    print('-------------------')


# --- FUNÇÃO PRINCIPAL PARA INICIAR O BOT ---

async def main():
    """Função principal que carrega os cogs e inicia a conexão do bot."""
    # Verifica se o token foi carregado com sucesso
    if TOKEN is None:
        print("ERRO: O DISCORD_TOKEN não foi encontrado. Certifique-se de que o ficheiro .env existe e está correto.")
        return
    
    # Usa um gerenciador de contexto para garantir que o bot se conecta e desconecta de forma segura
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

# --- INICIA A EXECUÇÃO DO BOT ---
# Esta é a forma moderna e recomendada de iniciar um bot com asyncio.
if __name__ == '__main__':
    asyncio.run(main())