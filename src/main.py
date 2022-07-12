# libraries
import discord
from discord.ext.commands import Bot
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from os import getenv
from online import keep_alive
from json import dump, load
from time import time
from random import randint
import asyncio

# setting up
bal_file = "balances.json"
job_file = "jobs.json"
job_list = {
    "Unemployed": {"Pay": 0, "Cost": 0}, 
    "Maid": {"Pay": 25, "Cost": 0}, 
    "Youtuber": {"Pay": 40, "Cost": 500}
}
intents = discord.Intents.default()
intents.members = True
embed_color = 0xffcd02
bot = Bot(command_prefix="$m ", intents=intents, help_command=None)

# adding money
async def _add(user, money):
    balances = load(open(bal_file))
    idstr = str(user)
    if not (idstr in balances.keys()):
        balances[idstr] = 0
    balances[idstr] += money
    if balances[idstr] < 0:
        balances[idstr] = 0
    dump(balances, open(bal_file, "w"))

# seeing if bot successfully logged on
@bot.event
async def on_ready():
    print("success, logged in as " + str(bot.user.id))

# give random chance to win 1-10$
@bot.event
async def on_message(message):
    if int(time() * 1000) % 20 == 0: # i know, it's only pseudorandom
        amount = randint(1, 10)
        embed = discord.Embed(
            title=f"**Congratulations {message.author}, you just randomly won {amount} coins!**",
            color=embed_color
        )
        await _add(message.author.id, amount)
        await message.reply(embed=embed)
    await bot.process_commands(message) # process commands

# new help command
@bot.group()
async def help(ctx):
    embed = discord.Embed(
        title="***Midas Help***",               
        description="""
        **Version 0.1: First Launch**
        
*$m help* - This help command.
*$m bal* - Shows your balance.
*$m job* - Manages jobs.
        """,
        color=embed_color
    )
    footer = "A day in Midas is 1 hour in real life."
    # embed.set_footer(text=footer)
    await ctx.reply(embed=embed)

# balance
@bot.command()
async def bal(ctx, user:discord.User=None):
    balances = load(open(bal_file))
    idstr = str(ctx.message.author.id)
    if not (idstr in balances.keys()):
        balances[idstr] = 0
        dump(balances, open(bal_file, "w"))
    if user != None:
        embed = discord.Embed(
            title=f"***{user}'s balance***",
            description=f"Their current balance is: {str(balances[str(user.id)])}.",
            color=embed_color
        )
        await ctx.reply(embed=embed)
        return
    embed = discord.Embed(
        title=f"***{ctx.message.author}'s balance***",
        description=f"Your current balance is: {str(balances[idstr])} coins.",
        color=embed_color
    )
    await ctx.reply(embed=embed)

# job group command
@bot.group()
async def job(ctx):
    if ctx.invoked_subcommand is None:
        embed = discord.Embed(
            title="***What job do you want to apply for?***",
            description="Type *$m job list* to get a list of jobs. Type *$m job apply <job>* to apply for a job. Type *$m job work once* you have a job.",
            color=embed_color
        )
        await ctx.reply(embed=embed)

# job list
@job.command()
async def list(ctx):
    embed = discord.Embed(
        title="***Job List***",
        description="""
        Type *$m job apply <job>* in order to be hired.
        
        **Job List:**
        - Unemployed:
            Salary: Cannot work
            Requirements: None
        - Maid:
            Salary: 25$ per task
            Requirements: None
        - Youtuber:
            Salary: 40$ per task
            Requirements: Needs to have at least 500$ to apply
        
More jobs coming soon!
        """,
        color=embed_color
    )
    footer = "You get paid every Midas day, or 1 hour in real time."
    # embed.set_footer(text=footer)
    await ctx.reply(embed=embed)

# apply for jobs
@job.command()
async def apply(ctx, job=None):
    job = job.capitalize() if job else job
    jobs = load(open(job_file))
    balances = load(open(bal_file))
    idstr = str(ctx.message.author.id)
    if not (idstr in jobs.keys()):
        jobs[idstr] = "Unemployed"
    if job is None:
        embed = discord.Embed(
            title="***Uh oh, you might want to choose a job.***",
            description="**Choose a job listed in *$m job list*. After do *$m job apply <your job here>.***",
            color=embed_color
        )
        await ctx.reply(embed=embed)
        return
    if not (job in job_list.keys()):
        embed = discord.Embed(
            title="***Uh oh, looks like you picked an unknown job.***",
            description="**Be sure that there was no spelling mistake. Try again after.**",
            color=embed_color
        )
        await ctx.reply(embed=embed)
        return
    if balances[idstr] <= job_list[job]["Cost"]:
        missing = job_list[job]["Cost"] - balances[idstr]
        embed = discord.Embed(
            title=f"***Sorry you cannot afford this, you need {str(missing)} coins.***",
            color=embed_color
        )
        await ctx.reply(embed=embed)
        return
    await _add(ctx.message.author.id, -job_list[job]["Cost"])
    jobs[idstr] = job
    congrats = "Congrats on your new job!" if job != "Unemployed" else ""
    embed = discord.Embed(
        title=f"**You successfully applied to be {job.lower()}. {congrats} **",
        color=embed_color
    )
    await ctx.reply(embed=embed)
    dump(balances, open(bal_file, "w"))
    dump(jobs, open(job_file, "w"))

@job.command()
@commands.cooldown(1, 20, commands.BucketType.user)
async def work(ctx):
    jobs = load(open(job_file))
    idstr = str(ctx.message.author.id)
    if jobs[idstr] == "Unemployed":
        embed = discord.Embed(
            title="***Uh oh, looks like you don't have a job.***",
            description="**You cannot work without a job, do *$m job apply <your job here>* to get one.**",
            color=embed_color
        )
        await ctx.reply(embed=embed)
        return
    x, y = randint(0, 20), randint(0, 20)
    operator = ("+", "-", "*")[randint(0, 2)]
    expression = f"{x}{operator}{y}"
    result = str(eval(expression))
    salary = job_list[jobs[idstr]]["Pay"]
    embed = discord.Embed(
        title=f"**What is {expression}?**",
        description=f"Answer correctly within 30 seconds for {salary} coins."
    )
    await ctx.reply(embed=embed)
    try:
        message = await bot.wait_for("message", check=lambda message: message.author.id == ctx.message.author.id, timeout=30)
    except asyncio.TimeoutError:
        embed = discord.Embed(
            title="***Uh oh, you didn't respond in time...***",
            description=f"You couldn't respond in time, anyways the answer was {result}.",
            color=embed_color
        )
        footer = "lol imagine not being able to do a simple operation"
        embed.set_footer(text=footer)
        await ctx.reply(embed=embed)
        return
    else:
        if message.content == result:
            await _add(ctx.message.author.id, salary)
            embed = discord.Embed(
                title=f"***Congrats! You earned {salary} coins.***",
                color=embed_color
            )
            await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(
                title=f"***You guessed wrong. The answer was {result}.***",
                color=embed_color
            )
            await ctx.reply(embed=embed)

# cooldown
@work.error
async def _error_work(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(
            title=f"***This command is on cooldown. Retry after {round(error.retry_after)} seconds.***",
            color=embed_color
        )
        footer = "error: discord.ext.commands.CommandOnCooldown"
        embed.set_footer(text=footer)
        await ctx.reply(embed=embed)

# run bot
keep_alive()
bot.run(getenv("token"))  # token is private for security reasons
