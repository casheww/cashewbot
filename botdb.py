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


async def dump_guild_data(db, guild_id: int, info: str):
    data = await get_guild_data(db, guild_id)

    async with db.cursor() as c:

        if data:
            await c.execute('UPDATE guilds SET info=? WHERE id=?;',
                            [info, guild_id])

        else:
            await c.execute('INSERT INTO guilds VALUES (?, ?);', [guild_id, info])
    await db.commit()


async def delete_guild(db, guild_id: int):
    async with db.cursor() as c:
        await c.execute('DELETE FROM guilds WHERE id=?;', [guild_id])
    await db.commit()


async def get_announce(db, guild_id: int):
    """ returns list: [guild_id, wh_url, wh_id] """

    async with db.cursor() as c:
        await c.execute('SELECT * FROM announce WHERE guild=?', [guild_id])
        announce_data = await c.fetchall()

        try:
            return announce_data[0]
        except IndexError:
            return announce_data


async def get_all_announce(db):
    """ returns list: [guild_id, wh_url, wh_id] """

    async with db.cursor() as c:
        await c.execute('SELECT * FROM announce')
        data = await c.fetchall()

        return data


async def dump_announce(db, guild_id: int, wh_url: str, wh_id: int):
    data = await get_announce(db, guild_id)

    async with db.cursor() as c:
        if data:
            await c.execute('UPDATE announce SET url=?, id=? WHERE guild=?;', [wh_url, wh_id, guild_id])

        else:
            await c.execute('INSERT INTO announce VALUES (?, ?, ?)', [guild_id, wh_url, wh_id])
    await db.commit()


async def delete_announce(db, guild_id):
    async with db.cursor() as c:
        await c.execute('DELETE FROM announce WHERE guild=?;', [guild_id])
    await db.commit()


