import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta, timezone

class TomaLerda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Debug: Print todas as mensagens para verificar se está detectando
        print(f"Mensagem detectada: '{message.content}' de {message.author}")
        
        # Ignora mensagens do próprio bot
        if message.author == self.bot.user:
            print("Ignorando mensagem do bot")
            return
        
        # Verifica se a mensagem é exatamente "tomalerda"
        if message.content.lower() == "tomalerda":
            print(f"Comando tomalerda detectado de {message.author}")
            print(f"Canal: {message.channel.name}")
            print(f"Servidor: {message.guild.name}")
            # Verifica se o bot tem permissão para gerenciar mensagens
            if not message.channel.permissions_for(message.guild.me).manage_messages:
                print("Bot não tem permissão para gerenciar mensagens")
                return  # Falha silenciosamente
            
            print("Iniciando processo de limpeza...")
            
            try:
                # Busca as últimas 1000 mensagens do canal
                messages_to_delete = []
                
                print("Buscando mensagens...")
                async for msg in message.channel.history(limit=1000):
                    if msg.author.id == message.author.id:
                        messages_to_delete.append(msg)
                
                print(f"Encontradas {len(messages_to_delete)} mensagens para deletar")
                
                if not messages_to_delete:
                    print("Nenhuma mensagem encontrada para deletar")
                    return  # Não faz nada se não encontrar mensagens
                
                # Separa mensagens por idade (Discord só permite bulk delete em mensagens de até 14 dias)
                now = datetime.now(timezone.utc)
                two_weeks_ago = now - timedelta(days=14)
                
                recent_messages = []
                old_messages = []
                
                for msg in messages_to_delete:
                    if msg.created_at > two_weeks_ago:
                        recent_messages.append(msg)
                    else:
                        old_messages.append(msg)
                
                # Apaga mensagens recentes usando bulk_delete (mais rápido)
                if recent_messages:
                    print(f"Deletando {len(recent_messages)} mensagens recentes...")
                    # Divide em grupos de até 100 mensagens (limite do bulk_delete)
                    for i in range(0, len(recent_messages), 100):
                        batch = recent_messages[i:i+100]
                        await message.channel.delete_messages(batch)
                        print(f"Deletado batch de {len(batch)} mensagens")
                        await asyncio.sleep(0.5)  # Pequeno delay entre batches
                
                # Apaga mensagens antigas individualmente
                if old_messages:
                    print(f"Deletando {len(old_messages)} mensagens antigas...")
                    for msg in old_messages:
                        try:
                            await msg.delete()
                            await asyncio.sleep(0.1)  # Delay para evitar rate limit
                        except Exception as e:
                            print(f"Erro ao deletar mensagem antiga: {e}")
                            continue  # Ignora erros silenciosamente
                
                print("Processo de limpeza concluído!")
                            
            except Exception as e:
                # Falha silenciosamente em caso de erro
                print(f"Erro no processo de limpeza: {e}")
                return

async def setup(bot):
    await bot.add_cog(TomaLerda(bot))