import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta, timezone

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
                return
            
            try:
                # Coleta todas as mensagens do usuário em uma única passada
                user_messages = []
                now = datetime.now(timezone.utc)
                two_weeks_ago = now - timedelta(days=14)
                
                # Busca mensagens de forma mais eficiente
                async for msg in message.channel.history(limit=1000):
                    if msg.author.id == message.author.id:
                        user_messages.append(msg)
                
                if not user_messages:
                    return
                
                # Separa mensagens por idade em uma única iteração
                recent_messages = []
                old_messages = []
                
                for msg in user_messages:
                    if msg.created_at > two_weeks_ago:
                        recent_messages.append(msg)
                    else:
                        old_messages.append(msg)
                
                # Cria tasks assíncronas para processamento paralelo
                tasks = []
                
                # Processa mensagens recentes em paralelo (chunks de 100)
                if recent_messages:
                    for i in range(0, len(recent_messages), 100):
                        batch = recent_messages[i:i+100]
                        tasks.append(self._delete_batch(message.channel, batch))
                
                # Executa todos os batches em paralelo
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                
                # Processa mensagens antigas de forma otimizada
                if old_messages:
                    await self._delete_old_messages_optimized(old_messages)
                    
            except Exception:
                return

    async def _delete_batch(self, channel, messages):
        """Deleta um lote de mensagens de forma assíncrona"""
        try:
            await channel.delete_messages(messages)
        except Exception:
            # Se bulk_delete falhar, tenta individualmente
            for msg in messages:
                try:
                    await msg.delete()
                except Exception:
                    continue

    async def _delete_old_messages_optimized(self, old_messages):
        """Deleta mensagens antigas de forma otimizada com paralelismo controlado"""
        # Processa em chunks menores com semáforo para controlar concorrência
        semaphore = asyncio.Semaphore(5)  # Máximo 5 deletions simultâneas
        
        async def delete_with_semaphore(msg):
            async with semaphore:
                try:
                    await msg.delete()
                except Exception:
                    pass
        
        # Cria tasks para todas as mensagens antigas
        tasks = [delete_with_semaphore(msg) for msg in old_messages]
        
        # Executa com limite de concorrência
        await asyncio.gather(*tasks, return_exceptions=True)

async def setup(bot):
    await bot.add_cog(TomaLerda(bot))