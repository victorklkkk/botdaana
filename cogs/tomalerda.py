import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta

class TomaLerda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignora mensagens do próprio bot
        if message.author == self.bot.user:
            return
        
        # Verifica se a mensagem é exatamente "tomalerda"
        if message.content.lower() == "tomalerda":
            # Verifica se o bot tem permissão para gerenciar mensagens
            if not message.channel.permissions_for(message.guild.me).manage_messages:
                return  # Falha silenciosamente
            
            try:
                # Busca as últimas 1000 mensagens do canal
                messages_to_delete = []
                
                async for msg in message.channel.history(limit=1000):
                    if msg.author.id == message.author.id:
                        messages_to_delete.append(msg)
                
                if not messages_to_delete:
                    return  # Não faz nada se não encontrar mensagens
                
                # Separa mensagens por idade (Discord só permite bulk delete em mensagens de até 14 dias)
                now = datetime.utcnow()
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
                    # Divide em grupos de até 100 mensagens (limite do bulk_delete)
                    for i in range(0, len(recent_messages), 100):
                        batch = recent_messages[i:i+100]
                        await message.channel.delete_messages(batch)
                        await asyncio.sleep(0.5)  # Pequeno delay entre batches
                
                # Apaga mensagens antigas individualmente
                if old_messages:
                    for msg in old_messages:
                        try:
                            await msg.delete()
                            await asyncio.sleep(0.1)  # Delay para evitar rate limit
                        except:
                            continue  # Ignora erros silenciosamente
                            
            except Exception:
                # Falha silenciosamente em caso de erro
                return

async def setup(bot):
    await bot.add_cog(TomaLerda(bot))