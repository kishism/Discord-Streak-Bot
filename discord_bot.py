import discord
from discord.ext import commands
import json
from datetime import datetime

# Set up the bot with a command prefix
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# File to store user data
data_file = "user_data.json"

# Load user data from the file
def load_data():
    try:
        with open(data_file, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Save user data to the file
def save_data(data):
    with open(data_file, "w") as f:
        json.dump(data, f, indent=4)

# Helper function to check if a user has logged in today
def is_new_day(last_login):
    today = datetime.today().date()
    return last_login != today

# Track user login streak and assign rewards
@bot.event
async def on_message(message):
    if message.author.bot:
        return  # Ignore bot messages

    user_id = str(message.author.id)
    data = load_data()

    # Get today's date
    today = datetime.today().date()

    if user_id not in data:
        # New user: Initialize their data
        data[user_id] = {
            "last_login": str(today),
            "login_streak": 1,
            "rewards": 0
        }
    else:
        # Existing user: Check if they've logged in today
        last_login = datetime.strptime(data[user_id]["last_login"], "%Y-%m-%d").date()

        if is_new_day(last_login):
            # New day: Update login streak
            data[user_id]["login_streak"] += 1
            data[user_id]["last_login"] = str(today)

            # Assign rewards based on streak
            streak = data[user_id]["login_streak"]
            if streak % 7 == 0:  # Reward every week
                data[user_id]["rewards"] += 50
                await message.author.send(f"Congratulations! You've reached a {streak}-day streak and earned 50 points!")
            elif streak % 30 == 0:  # Reward every month
                data[user_id]["rewards"] += 200
                await message.author.send(f"Awesome! You've reached a {streak}-day streak and earned 200 points!")

    # Save the updated data after changes
    save_data(data)

    # Respond to the user with their login streak
    await message.channel.send(f"{message.author.mention}, your current login streak is {data[user_id]['login_streak']} days!")

    # Allow commands to work
    await bot.process_commands(message)

# Command to check rewards
@bot.command(name="rewards")
async def check_rewards(ctx):
    user_id = str(ctx.author.id)
    data = load_data()

    if user_id in data:
        rewards = data[user_id]["rewards"]
        streak = data[user_id]["login_streak"]

        # Check if the user has a badge for their streak
        embed = discord.Embed(
            title=f"{ctx.author.display_name}'s Rewards", 
            description=f"You have {rewards} reward points!", 
            color=discord.Color.green()
        )

        # Check streak and assign corresponding badge image
        if streak >= 7 and streak % 7 == 0:  # Badge for 7-day streak
            badge_image_path = r"C:\Users\USER\Downloads\pinterests\furina.jpg"  # Local path
            try:
                badge_image = discord.File(badge_image_path, filename="furina.jpg")
                embed.set_image(url="attachment://furina.jpg")  # Embedding the image
                await ctx.send(f"{ctx.author.mention}, here's your badge for a {streak}-day streak!", embed=embed, file=badge_image)
            except FileNotFoundError:
                await ctx.send(f"{ctx.author.mention}, the badge image could not be found.")
        elif streak >= 30 and streak % 30 == 0:  # Badge for 30-day streak
            badge_image_path = r"C:\Users\USER\Downloads\pinterests\download.jpg"  # Local path
            try:
                badge_image = discord.File(badge_image_path, filename="download.jpg")
                embed.set_image(url="attachment://download.jpg")  # Embedding the image
                await ctx.send(f"{ctx.author.mention}, here's your badge for a {streak}-day streak!", embed=embed, file=badge_image)
            except FileNotFoundError:
                await ctx.send(f"{ctx.author.mention}, the badge image could not be found.")
        else:
            await ctx.send(f"{ctx.author.mention}, you have {rewards} reward points!")
    else:
        await ctx.send(f"{ctx.author.mention}, you haven't started your login streak yet!")

# Run the bot
bot.run('MYBOTTOKEN')  # Replace with your bot's token