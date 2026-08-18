import aiohttp


async def validate(token):
    headers = {'Authorization': token, 'Content-Type': 'application/json'}
    timeout = aiohttp.ClientTimeout(total=10, connect=5)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get('https://discord.com/api/v9/users/@me', headers=headers) as resp:
                if resp.status != 200:
                    return None
                user = await resp.json()
                return user.get('username') or user.get('global_name')
    except Exception:
        return None