import mcstatus


def server_info(ip, port):
    server = mcstatus.MinecraftServer.lookup(f"{ip}:{port}")
    status = server.status()
    query = server.query()

    info = {
        "title": query.map,
        "fields": [
            {
                "name": f"{query.players.online}/{query.players.max} players",
                "value": "Names not provided",
                "inline": False
            },
        ],
        "footer": {
            "text": f"Minecraft server - {status.version.name}"
        }
    }
    if query.players.online != 0:
        info["fields"][0]["value"] = "\n".join(
            [f"‣ {n}" for n in query.players.names])
    else:
        info["fields"][0]["value"] = "No-one's home :("

    return info, status.favicon
