import discord
from discord.ext import commands
import json
import random
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "users.json"

level_roles = {
    3: "🧀꒰Lv.03꒱",
    10: "🧀꒰Lv.10꒱",
    20: "🧀꒰Lv.20꒱",
    30: "🧀꒰Lv.30꒱",
    40: "🧀꒰Lv.40꒱",
    50: "🧀꒰Lv.50꒱",
    60: "🧀꒰Lv.60꒱",
    70: "🧀꒰Lv.70꒱",
    80: "🧀꒰Lv.80꒱",
    90: "🧀꒰Lv.90꒱",
    100: "🧀꒰Lv.100꒱"
}


def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


data = load_data()


def get_user(user_id):
    user_id = str(user_id)

    if user_id not in data:
        data[user_id] = {
            "cheese": 100,
            "xp": 0,
            "level": 1,
            "last_daily": None
        }

    return data[user_id]


async def update_level_role(member, new_level):

    if member.guild is None:
        return

    give_role_name = level_roles.get(new_level)

    if not give_role_name:
        return

    give_role = discord.utils.get(member.guild.roles, name=give_role_name)

    if give_role is None:
        return

    remove_roles = []

    for role_name in level_roles.values():
        role = discord.utils.get(member.guild.roles, name=role_name)

        if role and role in member.roles and role.name != give_role_name:
            remove_roles.append(role)

    if remove_roles:
        await member.remove_roles(*remove_roles)

    if give_role not in member.roles:
        await member.add_roles(give_role)


@bot.event
async def on_ready():
    print(f"{bot.user} 로그인 완료")


@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if message.guild is None:
        return

    user = get_user(message.author.id)

    user["xp"] += 5
    need_xp = user["level"] * 100

    if user["xp"] >= need_xp:

        user["xp"] = 0
        user["level"] += 1

        await message.channel.send(
            f"{message.author.mention} 🎉 레벨업! 현재 레벨: **Lv.{user['level']}**"
        )

        await update_level_role(message.author, user["level"])

        if user["level"] in level_roles:
            await message.channel.send(
                f"{message.author.mention} 🧀 새 역할 지급: **{level_roles[user['level']]}**"
            )

    save_data(data)
    await bot.process_commands(message)


@bot.command(name="치즈", aliases=["돈"])
async def cheese(ctx):

    user = get_user(ctx.author.id)

    await ctx.send(
        f"{ctx.author.mention}님의 치즈는 **{user['cheese']}🧀** 입니다."
    )


@bot.command()
async def 출석(ctx):

    user = get_user(ctx.author.id)

    today = datetime.utcnow().strftime("%Y-%m-%d")

    if user["last_daily"] == today:
        await ctx.send(f"{ctx.author.mention} 오늘은 이미 출석했어요.")
        return

    user["last_daily"] = today
    user["cheese"] += 50

    save_data(data)

    await ctx.send(f"{ctx.author.mention} 출석 완료! **50🧀** 지급됐어요.")


@bot.command()
async def 도박(ctx, amount: int):

    user = get_user(ctx.author.id)

    if amount <= 0:
        await ctx.send("1 이상만 입력하세요.")
        return

    if user["cheese"] < amount:
        await ctx.send("치즈가 부족해요.")
        return

    if random.randint(1, 100) <= 50:

        user["cheese"] += amount
        result = f"성공! **{amount}🧀** 획득!"

    else:

        user["cheese"] -= amount
        result = f"실패! **{amount}🧀** 잃었어요."

    save_data(data)

    await ctx.send(f"{ctx.author.mention} 🎰 {result}")


@bot.command()
async def 랭킹(ctx):

    ranking_data = sorted(
        data.items(),
        key=lambda x: x[1].get("cheese", 0),
        reverse=True
    )

    msg = "🏆 **치즈 랭킹 TOP 10**\n\n"

    count = 0

    for user_id, user_info in ranking_data:

        try:

            member = await bot.fetch_user(int(user_id))

            count += 1

            msg += f"{count}. {member.name} - {user_info.get('cheese', 0)}🧀\n"

            if count >= 10:
                break

        except:
            continue

    await ctx.send(msg)


@bot.command()
async def 레벨(ctx):

    user = get_user(ctx.author.id)

    need_xp = user["level"] * 100

    await ctx.send(
        f"{ctx.author.mention} 현재 레벨: **Lv.{user['level']}** / XP: **{user['xp']} / {need_xp}**"
    )


@bot.command()
async def 레벨랭킹(ctx):

    ranking_data = sorted(
        data.items(),
        key=lambda x: (x[1].get("level", 1), x[1].get("xp", 0)),
        reverse=True
    )

    msg = "🥇 **레벨 랭킹 TOP 10**\n\n"

    count = 0

    for user_id, user_info in ranking_data:

        try:

            member = await bot.fetch_user(int(user_id))

            count += 1

            msg += (
                f"{count}. {member.name} - "
                f"Lv.{user_info.get('level', 1)} "
                f"({user_info.get('xp', 0)} XP)\n"
            )

            if count >= 10:
                break

        except:
            continue

    await ctx.send(msg)


bot.run("MTQ4MTIxMDEwNzYwMDU3MjUxNg.GLMZw-.3bnToRBWob6WAoSiIBMXeetCMBgeQY5sVGnIpg")