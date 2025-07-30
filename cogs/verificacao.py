# cogs/verificacao.py

import discord
from discord.ext import commands
from discord import ui
import re # Importamos a biblioteca de expressões regulares para extrair o ID

# --- CONFIGURAÇÕES DO COG ---
CANAL_LOGS_VERIFICACAO_ID = 1391938919842451472
CARGO_VERIFICADO_ID = 1391938919528009838  # <--- SUBSTITUA ESTE VALOR PELO ID DO CARGO

# --- CLASSES DA INTERFACE (VIEWS E MODAL) ---

class AdminApprovalView(ui.View):
    """View persistente que lê o ID do membro a partir do embed da mensagem."""
    def __init__(self):
        # O timeout=None garante que a View não expira.
        super().__init__(timeout=None)

    async def get_member_from_embed(self, interaction: discord.Interaction) -> discord.Member | None:
        """Extrai o ID do membro do rodapé do embed e retorna o objeto Member."""
        try:
            # Pega o primeiro embed da mensagem onde o botão foi clicado
            embed = interaction.message.embeds[0]
            # Extrai o texto do rodapé (ex: "ID do Membro: 12345...")
            footer_text = embed.footer.text
            # Usa regex para encontrar apenas os números no texto do rodapé
            member_id_match = re.search(r'\d+', footer_text)
            
            if not member_id_match:
                await interaction.response.send_message("Não foi possível encontrar o ID do membro no embed.", ephemeral=True)
                return None

            member_id = int(member_id_match.group(0))
            membro = interaction.guild.get_member(member_id)

            if not membro:
                await interaction.response.send_message("Membro original não encontrado. Ele pode ter saído do servidor.", ephemeral=True)
                return None
            
            return membro
        except (IndexError, AttributeError, ValueError) as e:
            await interaction.response.send_message(f"Erro ao processar o embed: {e}", ephemeral=True)
            return None


    @ui.button(label="Aprovar", style=discord.ButtonStyle.green, custom_id="aprovar_verificacao_ref_persistente")
    async def aprovar_callback(self, interaction: discord.Interaction, button: ui.Button):
        membro_a_verificar = await self.get_member_from_embed(interaction)
        if not membro_a_verificar:
            return
        
        cargo = interaction.guild.get_role(CARGO_VERIFICADO_ID)
        
        if cargo:
            await membro_a_verificar.add_roles(cargo)
            await interaction.response.send_message(f"✅ O usuário {membro_a_verificar.mention} foi verificado por {interaction.user.mention}.", ephemeral=True)
            for item in self.children:
                item.disabled = True
            await interaction.message.edit(view=self)
        else:
            await interaction.response.send_message(f"⚠️ O cargo com o ID configurado não foi encontrado.", ephemeral=True)

    @ui.button(label="Reprovar", style=discord.ButtonStyle.red, custom_id="reprovar_verificacao_ref_persistente")
    async def reprovar_callback(self, interaction: discord.Interaction, button: ui.Button):
        membro_a_verificar = await self.get_member_from_embed(interaction)
        if not membro_a_verificar:
            return

        await interaction.response.send_message(f"❌ O pedido de verificação de {membro_a_verificar.mention} foi reprovado.", ephemeral=True)
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(view=self)


class VerificationModal(ui.Modal, title="Formulário de Verificação"):
    referencia = ui.TextInput(label="Quem você conhece no servidor?", placeholder="Escreva o nome de usuário (ex: joao123)", required=True, style=discord.TextStyle.short)
    async def on_submit(self, interaction: discord.Interaction):
        canal_logs = interaction.client.get_channel(CANAL_LOGS_VERIFICACAO_ID)
        if not canal_logs:
            await interaction.response.send_message("Ocorreu um erro interno: Canal de logs não configurado.", ephemeral=True)
            return

        embed = discord.Embed(title="📥 Novo Pedido de Verificação", color=discord.Color.blue())
        embed.add_field(name="Membro a verificar", value=interaction.user.mention, inline=False)
        embed.add_field(name="Diz conhecer", value=self.referencia.value, inline=False)
        # O rodapé é a chave para a persistência!
        embed.set_footer(text=f"ID do Membro: {interaction.user.id}")

        # Agora criamos a AdminApprovalView sem passar nenhum argumento.
        await canal_logs.send(embed=embed, view=AdminApprovalView())
        
        await interaction.response.send_message("✅ Seu pedido foi enviado para a administração. Por favor, aguarde.", ephemeral=True)


class VerificationView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @ui.button(label="Iniciar Verificação", style=discord.ButtonStyle.blurple, custom_id="iniciar_verificacao_ref")
    async def button_callback(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(VerificationModal())


# --- CLASSE PRINCIPAL DO COG ---
class VerificacaoCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Registamos AMBAS as views persistentes no arranque do bot.
        self.bot.add_view(VerificationView())
        self.bot.add_view(AdminApprovalView())

    @commands.group(name="setup")
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Comando de setup inválido. Use `!setup verif`.", delete_after=10)

    @setup.command(name="verif")
    @commands.has_permissions(administrator=True)
    async def setup_verif(self, ctx: commands.Context):
        embed = discord.Embed(
            title="Sistema de Verificação por Referência",
            description="Para ter acesso ao servidor, inicie o processo de verificação.",
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed, view=VerificationView())
        await ctx.message.delete()

# --- FUNÇÃO SETUP DO COG ---
async def setup(bot: commands.Bot):
    await bot.add_cog(VerificacaoCog(bot))