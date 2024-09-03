import discord
from discord.ext import commands
import aiosqlite

intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

#Ayarlar
SEVIYELER = {
    1: 10,    # 1. seviye
    2: 20,    # 2. seviye
    3: 50,    # 3. seviye
    4: 70,    # 4. seviye
    #5
    #6
    #7...
    
}
MESAJ_BASINA_XP = 10  # Mesaj attıkça kazanılan xp

async def veritabani_kurulum():
    async with aiosqlite.connect("seviyeler.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS kullanicilar (
                kullanici_id INTEGER PRIMARY KEY,
                xp INTEGER DEFAULT 0,
                seviye INTEGER DEFAULT 1
            )
        """)
        await db.commit()

async def xp_ekle(kullanici_id, miktar):
    async with aiosqlite.connect("seviyeler.db") as db:
        cursor = await db.execute("SELECT xp, seviye FROM kullanicilar WHERE kullanici_id = ?", (kullanici_id,))
        result = await cursor.fetchone()

        if result:
            xp, seviye = result
            xp += miktar

            #Level check
            yeni_seviye = seviye
            for seviye_no, gerekli_xp in SEVIYELER.items():
                if xp >= gerekli_xp:
                    yeni_seviye = seviye_no
                else:
                    break

            if yeni_seviye > seviye:
                await db.execute("UPDATE kullanicilar SET xp = ?, seviye = ? WHERE kullanici_id = ?", (xp, yeni_seviye, kullanici_id))
                await db.commit()
                return yeni_seviye
            else:
                await db.execute("UPDATE kullanicilar SET xp = ? WHERE kullanici_id = ?", (xp, kullanici_id))
                await db.commit()
        else:
            await db.execute("INSERT INTO kullanicilar (kullanici_id, xp) VALUES (?, ?)", (kullanici_id, miktar))
            await db.commit()
        return None

@bot.event
async def on_ready():
    await veritabani_kurulum()
    print(f'{bot.user} olarak giriş yapıldı.')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    kullanici_id = message.author.id
    seviye_kanali = bot.get_channel(1280516363206787124)  #Seviye mesajları için kanal id

    seviye_atlama = await xp_ekle(kullanici_id, MESAJ_BASINA_XP)  #Mesaj başına kazanılan xp

    if seviye_atlama:
        await seviye_kanali.send(f'🎉 {message.author.mention} {seviye_atlama} seviyesine ulaştı!')

    await bot.process_commands(message)

bot.run('')  #Token
