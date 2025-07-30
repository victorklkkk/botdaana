# cogs/verificacao.py

import discord
from discord.ext import commands
from discord import ui

# --- CONFIGURAÇÃO DO COG ---
# !! IMPORTANTE: SUBSTITUA O VALOR ABAIXO PELO ID DO SEU CANAL DE LOGS DE VERIFICAÇÃO !!
CANAL_LOGS_VERIFICACAO_ID = 123456789012345678


# --- CLASSES DA INTERFACE (VIEWS E MODAL) ---
# Estas classes definem os botões e a janela de formulário.

class AdminApprovalView(ui.View):
    """View com os botões de Aprovar/Reprovar para os Admins."""
    def __init__(self, membro_a_verificar_id: int):
        super().__init__(timeout=None) # Timeout None para que os botões não expirem.
        self.membro_a_verificar_id = membro_a_verificar_id

    async def get_member(self, interaction: discord.Interaction) -> discord.Member | None:
        """Helper para encontrar o membro no servidor."""
        membro = interaction.guild.get_member(self.membro_a_verificar_id)
        if not membro:
            await interaction.response.send_message("Não foi possível encontrar o membro original. Ele pode ter saído do servidor.", ephemeral=True)
            return None
        return membro

    @ui.button(label="Aprovar", style=discord.ButtonStyle.green, custom_id="aprovar_verificacao_ref")
    async def aprovar_callback(self, interaction: discord.Interaction, button: ui.Button):
        membro_a_verificar = await self.get_member(interaction)
        if not membro_a_verificar:
            return

        nome_cargo = "Verificado"
        cargo = discord.utils.get(interaction.guild.roles, name=nome_cargo)
        
        if cargo:
            try:
                await membro_a_verificar.add_roles(cargo)
                await interaction.response.send_message(f"✅ O usuário {membro_a_verificar.mention} foi verificado por {interaction.user.mention}.", ephemeral=True)
                
                # Desativa os botões para indicar que a ação foi concluída.
                for item in self.children:
                    item.disabled = True
                await interaction.message.edit(view=self)
            except discord.Forbidden:
                await interaction.response.send_message("❌ Erro: Não tenho permissão para atribuir cargos.", ephemeral=True)
        else:
            await interaction.response.send_message(f"⚠️ O cargo `{nome_cargo}` não foi encontrado. Por favor, crie-o primeiro.", ephemeral=True)

    @ui.button(label="Reprovar", style=discord.ButtonStyle.red, custom_id="reprovar_verificacao_ref")
    async def reprovar_callback(self, interaction: discord.Interaction, button: ui.Button):
        membro_a_verificar = await self.get_member(interaction)
        if not membro_a_verificar:
            return

        await interaction.response.send_message(f"❌ O pedido de verificação de {membro_a_verificar.mention} foi reprovado por {interaction.user.mention}.", ephemeral=True)
        
        # Desativa os botões.
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(view=self)


class VerificationModal(ui.Modal, title="Formulário de Verificação"):
    """O formulário (pop-up) que o usuário preenche."""
    referencia = ui.TextInput(label="Quem você conhece no servidor?", placeholder="Escreva o nome de usuário (ex: joao123)", required=True, style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        canal_logs = interaction.client.get_channel(CANAL_LOGS_VERIFICACAO_ID)
        if not canal_logs:
            await interaction.response.send_message("Ocorreu um erro interno: Canal de logs não configurado.", ephemeral=True)
            return

        embed = discord.Embed(title="📥 Novo Pedido de Verificação", color=discord.Color.blue())
        embed.add_field(name="Membro a verificar", value=interaction.user.mention, inline=False)
        embed.add_field(name="Diz conhecer", value=self.referencia.value, inline=False)
        embed.set_footer(text=f"ID do Membro: {interaction.user.id}")

        view_admin = AdminApprovalView(membro_a_verificar_id=interaction.user.id)
        await canal_logs.send(embed=embed, view=view_admin)
        
        await interaction.response.send_message("✅ O seu pedido foi enviado para a administração. Por favor, aguarde.", ephemeral=True)


class VerificationView(ui.View):
    """A View principal com o botão 'Iniciar Verificação' que fica na mensagem."""
    def __init__(self):
        super().__init__(timeout=None) # Timeout None torna a View persistente.

    @ui.button(label="Iniciar Verificação", style=discord.ButtonStyle.blurple, custom_id="iniciar_verificacao_ref")
    async def button_callback(self, interaction: discord.Interaction, button: ui.Button):
        modal = VerificationModal()
        await interaction.response.send_modal(modal)


# --- CLASSE PRINCIPAL DO COG ---

class VerificacaoCog(commands.Cog):
    """Cog que agrupa todos os comandos e lógicas de verificação."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Adicionamos a View persistente aqui.
        # O bot irá "lembrar-se" dela mesmo que seja reiniciado.
        self.bot.add_view(VerificationView())

    @commands.command(name="setup_verificacao_ref")
    @commands.has_permissions(administrator=True)
    async def setup_verificacao_ref(self, ctx: commands.Context):
        """Cria a mensagem de verificação por referência no canal atual."""
        embed = discord.Embed(
            title="Sistema de Verificação por Referência",
            description="Para ter acesso ao servidor, por favor, inicie o processo de verificação.\n\nVocê precisará indicar o nome de um membro que já conhece e que está no servidor.",
            color=discord.Color.gold()
        )
        
        await ctx.send(embed=embed, view=VerificationView())
        
        # Apaga a mensagem de comando para manter o canal limpo.
        await ctx.message.delete()

    @setup_verificacao_ref.error
    async def setup_verificacao_ref_error(self, ctx: commands.Context, error: commands.CommandError):
        """Trata erros para o comando de setup."""
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Você não tem permissão de Administrador para usar este comando.", delete_after=10)


# --- FUNÇÃO SETUP DO COG ---
# Esta função é chamada pelo `main.py` para carregar o Cog.

async def setup(bot: commands.Bot):
    """Carrega o Cog de Verificação no bot."""
    await bot.add_cog(VerificacaoCog(bot))