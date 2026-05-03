import discord
from discord import app_commands
from discord.ext import commands
import asyncio

from bot.database import (
    add_transaction,
    get_transactions,
    get_categories,
    add_category,
    remove_category,
    get_category_totals,
    get_summary,
)
from bot.parser import parse_expense_message, extract_category_and_description, extract_date, clean_description
from bot.config import MAX_DESCRIPTION_WORDS


class ExpenseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.user_data = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        if not self.bot.user.mentioned_in(message):
            return
        
        content = message.content.replace(f"@{self.bot.user.name}", "").replace(f"@{self.bot.user.name}#{self.bot.user.discriminator}", "").strip()
        
        if not content or content.startswith("add "):
            return
        
        if content.startswith("list") or content.startswith("categories") or content.startswith("add-category") or content.startswith("remove-category") or content.startswith("help"):
            return
        
        await message.channel.TriggerTyping()
        
        parsed = parse_expense_message(content)
        
        if not parsed:
            await message.reply("I couldn't understand that. Try format like: `@bot spent $50 on lunch` or `@bot received $100 from freelance`")
            return
        
        categories = get_categories()
        
        transaction_type = parsed["transaction_type"]
        amount = parsed["amount"]
        raw_text = parsed.get("raw_text", "")
        
        category, description = extract_category_and_description(raw_text, categories)
        
        date_str, date_label = extract_date(content)
        
        self.bot.user_data[message.author.id] = {
            "step": "category" if category is None else "confirm",
            "transaction_type": transaction_type,
            "amount": amount,
            "category": category,
            "description": description,
            "date": date_str,
            "date_label": date_label,
        }
        
        if category is None:
            cat_list = ", ".join(categories)
            await message.reply(f"I detected: **{transaction_type}** of **${amount:.2f}** ({date_label})\n\nWhat category? (choose from: {cat_list})")
            return
        
        await self.send_confirmation(message)
    
    async def send_confirmation(self, message):
        user_data = self.bot.user_data.get(message.author.id)
        if not user_data:
            return
        
        category = user_data["category"]
        description = clean_description(user_data["description"], MAX_DESCRIPTION_WORDS)
        
        embed = discord.Embed(title="Confirm Transaction", color=0x3498db)
        embed.add_field(name="Type", value=user_data["transaction_type"].capitalize(), inline=True)
        embed.add_field(name="Amount", value=f"${user_data['amount']:.2f}", inline=True)
        embed.add_field(name="Category", value=category, inline=True)
        embed.add_field(name="Date", value=user_data["date_label"], inline=True)
        if description:
            embed.add_field(name="Description", value=description[:100], inline=False)
        
        msg = await message.reply(embed=embed, view=ConfirmView(self, message.author.id))
        self.bot.user_data[message.author.id]["message_id"] = msg.id

    @app_commands.command(name="add", description="Add an expense or income (e.g., spent $50 on lunch)")
    async def add_expense(self, interaction, text: str):
        parsed = parse_expense_message(text)
        
        if not parsed:
            await interaction.response.send_message("I couldn't understand that. Try: `spent $50 on lunch` or `received $100 from freelance`", ephemeral=True)
            return
        
        categories = get_categories()
        transaction_type = parsed["transaction_type"]
        amount = parsed["amount"]
        raw_text = parsed.get("raw_text", "")
        
        category, description = extract_category_and_description(raw_text, categories)
        date_str, date_label = extract_date(text)
        
        if category is None:
            cat_list = ", ".join(categories)
            await interaction.response.send_message(
                f"Detected: **{transaction_type}** of **${amount:.2f}** ({date_label})\n\nWhat category? (choose from: {cat_list})\n\nOr use `/add-category` to add a new one.",
                ephemeral=True
            )
            return
        
        description = clean_description(description, MAX_DESCRIPTION_WORDS)
        
        add_transaction(date_str, transaction_type, category, description, amount)
        
        embed = discord.Embed(title="Transaction Added", color=0x2ecc71)
        embed.add_field(name="Type", value=transaction_type.capitalize(), inline=True)
        embed.add_field(name="Amount", value=f"${amount:.2f}", inline=True)
        embed.add_field(name="Category", value=category, inline=True)
        embed.add_field(name="Date", value=date_label, inline=True)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="list", description="Show recent transactions")
    async def list_transactions(self, interaction, limit: int = 10):
        transactions = get_transactions(limit)
        
        if not transactions:
            await interaction.response.send_message("No transactions yet.", ephemeral=True)
            return
        
        embed = discord.Embed(title="Recent Transactions", color=0x3498db)
        
        for t in transactions[:10]:
            emoji = "📈" if t["transaction_type"] == "income" else "📉"
            embed.add_field(
                name=f"{emoji} {t['date']}",
                value=f"{t['category']}: ${t['amount']:.2f}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="categories", description="List all categories")
    async def list_categories(self, interaction):
        categories = get_categories()
        
        embed = discord.Embed(title="Categories", color=0x3498db)
        embed.description = ", ".join(categories)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="add-category", description="Add a new category")
    async def add_cat(self, interaction, name: str):
        categories = get_categories()
        
        if name in categories:
            await interaction.response.send_message(f"Category '{name}' already exists.", ephemeral=True)
            return
        
        add_category(name)
        await interaction.response.send_message(f"Category '{name}' added!")

    @app_commands.command(name="remove-category", description="Remove a category")
    async def remove_cat(self, interaction, name: str):
        categories = get_categories()
        
        if name not in categories:
            await interaction.response.send_message(f"Category '{name}' not found.", ephemeral=True)
            return
        
        remove_category(name)
        await interaction.response.send_message(f"Category '{name}' removed!")

    @app_commands.command(name="summary", description="Show expense summary")
    async def summary(self, interaction):
        summary = get_summary()
        
        embed = discord.Embed(title="Summary", color=0x3498db)
        embed.add_field(name="Total Income", value=f"${summary['total_income']:.2f}", inline=True)
        embed.add_field(name="Total Expense", value=f"${summary['total_expense']:.2f}", inline=True)
        embed.add_field(name="Balance", value=f"${summary['total_income'] - summary['total_expense']:.2f}", inline=True)
        
        await interaction.response.send_message(embed=embed)


class ConfirmView(discord.ui.View):
    def __init__(self, cog, user_id):
        super().__init__()
        self.cog = cog
        self.user_id = user_id

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success)
    async def confirm(self, interaction, button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your transaction.", ephemeral=True)
            return
        
        user_data = self.cog.bot.user_data.get(self.user_id)
        if not user_data:
            return
        
        category = user_data["category"]
        description = clean_description(user_data["description"], MAX_DESCRIPTION_WORDS)
        
        add_transaction(
            user_data["date"],
            user_data["transaction_type"],
            category,
            description,
            user_data["amount"]
        )
        
        embed = discord.Embed(title="Transaction Added!", color=0x2ecc71)
        embed.add_field(name="Type", value=user_data["transaction_type"].capitalize(), inline=True)
        embed.add_field(name="Amount", value=f"${user_data['amount']:.2f}", inline=True)
        embed.add_field(name="Category", value=category, inline=True)
        
        await interaction.response.edit_message(embed=embed, view=None)
        del self.cog.bot.user_data[self.user_id]

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction, button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your transaction.", ephemeral=True)
            return
        
        await interaction.response.edit_message(content="Transaction cancelled.", view=None)
        del self.cog.bot.user_data[self.user_id]