import aiosqlite
import json

# - - - - - -
#   JSON stuffed into an SQL database... the perfect bodge
# - - - - - -


async def get_guild_data(db, guild_id: int):
    """ returns dict with guild data """

    async with db.cursor() as c:
        await c.execute('SELECT * FROM guilds WHERE guild=?', [guild_id])
        guild_data = await c.fetchall()

        try:
            return json.loads(guild_data[0][1])
        except IndexError:
            return []


async def get_all_guilds(db):

    async with db.cursor() as c:
        await c.execute('SELECT * FROM guilds')
        data = await c.fetchall()

        return data


async def dump_guild_data(db, guild_id: int, info):
    data = await get_guild_data(db, guild_id)
    info = json.dumps(info)

    async with db.cursor() as c:

        if data:
            await c.execute('UPDATE guilds SET data=? WHERE guild=?;',
                            [info, guild_id])

        else:
            await c.execute('INSERT INTO guilds VALUES (?, ?);', [guild_id, info])
    await db.commit()


async def delete_guild(db, guild_id: int):
    async with db.cursor() as c:
        await c.execute('DELETE FROM guilds WHERE guild=?;', [guild_id])
    await db.commit()


async def get_bdays(db, guild_id: int):
    async with db.cursor() as c:
        await c.execute('SELECT * FROM bday WHERE guild=?', [guild_id])
        data = await c.fetchall()

        try:
            return json.loads(data[0][1])
        except IndexError:
            return None


async def dump_bdays(db, guild_id: int, data: str):
    base_data = await get_bdays(db, guild_id)

    async with db.cursor() as c:
        if not isinstance(base_data, type(None)):
            await c.execute('UPDATE bday SET data=? WHERE guild=?;', [data, guild_id])

        else:
            await c.execute('INSERT INTO bday VALUES (?, ?)', [guild_id, data])
    await db.commit()


async def delete_bdays(db, guild_id: int):
    async with db.cursor() as c:
        await c.execute('DELETE FROM bday WHERE guild=?;', [guild_id])
    await db.commit()


async def get_count_data(db, guild_id: int):

    async with db.cursor() as c:
        await c.execute('SELECT * FROM counting WHERE guild=?', [guild_id])
        counting_data = await c.fetchone()

        return counting_data


async def get_all_count_data(db):

    async with db.cursor() as c:
        await c.execute('SELECT * FROM counting')
        data = await c.fetchall()

        return data


async def dump_count_data(db, guild_id: int, channel_id: int, member_id: int,
                          num0: int, num1: int, fibonacci: int):
    data = await get_count_data(db, guild_id)

    async with db.cursor() as c:
        if data:
            await c.execute('UPDATE counting SET channel=?, member=?, '
                            'number0=?, number1=?, fibonacci=? WHERE guild=?',
                            [channel_id, member_id, num0, num1, fibonacci, guild_id])

        else:
            await c.execute('INSERT INTO counting VALUES (?, ?, ?, ?, ?, ?)',
                            [guild_id, channel_id, member_id, num0, num1, fibonacci])
    await db.commit()


async def delete_counting(db, guild_id):
    async with db.cursor() as c:
        await c.execute('DELETE FROM counting WHERE guild=?', [guild_id])
    await db.commit()
