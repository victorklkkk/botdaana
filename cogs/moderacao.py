# cogs/moderacao.py

import discord
from discord.ext import commands

class ModeracaoCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='nuke')
    @commands.has_permissions(manage_channels=True)
    async def nuke_channel(self, ctx):
        """
        Deleta o canal atual e recria com as mesmas configurações
        """
        try:
            # Guarda as informações do canal atual
            channel = ctx.channel
            
            # Salva todas as configurações do canal
            channel_data = {
                'name': channel.name,
                'category': channel.category,
                'position': channel.position,
                'topic': getattr(channel, 'topic', None),
                'slowmode_delay': getattr(channel, 'slowmode_delay', 0),
                'nsfw': getattr(channel, 'nsfw', False),
                'overwrites': channel.overwrites.copy() if hasattr(channel, 'overwrites') else {},
                'type': channel.type
            }
            
            # Configurações específicas para canais de voz
            if channel.type == discord.ChannelType.voice:
                channel_data.update({
                    'bitrate': channel.bitrate,
                    'user_limit': channel.user_limit,
                    'rtc_region': channel.rtc_region
                })
            
            # Envia mensagem de confirmação antes de deletar
            confirmation = await ctx.send("💣 **NUKE INICIADO!** Este canal será recriado em 3 segundos...")
            
            # Aguarda 3 segundos
            await confirmation.delete(delay=3)
            
            # Deleta o canal atual
            await channel.delete(reason=f"Nuke executado por {ctx.author}")
            
            # Recria o canal baseado no tipo
            if channel_data['type'] == discord.ChannelType.text:
                new_channel = await ctx.guild.create_text_channel(
                    name=channel_data['name'],
                    category=channel_data['category'],
                    position=channel_data['position'],
                    topic=channel_data['topic'],
                    slowmode_delay=channel_data['slowmode_delay'],
                    nsfw=channel_data['nsfw'],
                    overwrites=channel_data['overwrites'],
                    reason=f"Canal recriado via nuke por {ctx.author}"
                )
            
            elif channel_data['type'] == discord.ChannelType.voice:
                new_channel = await ctx.guild.create_voice_channel(
                    name=channel_data['name'],
                    category=channel_data['category'],
                    position=channel_data['position'],
                    bitrate=channel_data['bitrate'],
                    user_limit=channel_data['user_limit'],
                    overwrites=channel_data['overwrites'],
                    rtc_region=channel_data['rtc_region'],
                    reason=f"Canal recriado via nuke por {ctx.author}"
                )
            
            elif channel_data['type'] == discord.ChannelType.forum:
                new_channel = await ctx.guild.create_forum_channel(
                    name=channel_data['name'],
                    category=channel_data['category'],
                    position=channel_data['position'],
                    topic=channel_data['topic'],
                    slowmode_delay=channel_data['slowmode_delay'],
                    nsfw=channel_data['nsfw'],
                    overwrites=channel_data['overwrites'],
                    reason=f"Canal recriado via nuke por {ctx.author}"
                )
            
            else:
                # Para outros tipos de canal, usa método genérico
                new_channel = await ctx.guild.create_text_channel(
                    name=channel_data['name'],
                    category=channel_data['category'],
                    position=channel_data['position'],
                    overwrites=channel_data['overwrites'],
                    reason=f"Canal recriado via nuke por {ctx.author}"
                )
            
            # Envia mensagem de sucesso no novo canal
            if channel_data['type'] == discord.ChannelType.text or channel_data['type'] == discord.ChannelType.forum:
                embed = discord.Embed(
                    title="💥 CANAL NUKADO COM SUCESSO!",
                    description=f"Canal recriado por {ctx.author.mention}",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="📊 Detalhes",
                    value=f"**Nome:** {channel_data['name']}\n"
                          f"**Categoria:** {channel_data['category'].name if channel_data['category'] else 'Nenhuma'}\n"
                          f"**Tipo:** {channel_data['type'].name.title()}\n"
                          f"**Permissões:** {len(channel_data['overwrites'])} sobrescritas restauradas",
                    inline=False
                )
                embed.set_footer(text="Todas as mensagens anteriores foram permanentemente removidas.")
                
                await new_channel.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ Não tenho permissão para gerenciar canais!", delete_after=5)
        except discord.HTTPException as e:
            await ctx.send(f"❌ Erro ao recriar o canal: {e}", delete_after=5)
        except Exception as e:
            await ctx.send(f"❌ Erro inesperado: {e}", delete_after=5)

    @nuke_channel.error
    async def nuke_error(self, ctx, error):
        """Tratamento de erros específico para o comando nuke"""
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Você não tem permissão para usar este comando! (Necessário: Gerenciar Canais)", delete_after=5)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ Eu não tenho permissão para gerenciar canais!", delete_after=5)
        else:
            await ctx.send(f"❌ Erro ao executar comando: {error}", delete_after=5)

    # Futuramente, os seus outros comandos de moderação virão aqui.
    # Exemplo: @commands.command()


# A função setup que o bot procura em cada ficheiro de Cog.
async def setup(bot: commands.Bot):
    await bot.add_cog(ModeracaoCog(bot))