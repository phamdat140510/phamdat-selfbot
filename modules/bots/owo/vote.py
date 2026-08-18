import asyncio
import time

from modules.utils import topgg


class Vote:
    @staticmethod
    async def vote(client):
        if not client.can_run():
            return
        if time.time() < client.cooldown_vote:
            return
        bot_id = getattr(client.owo_bot, 'id', None)
        if not bot_id:
            return
        client.logger.info('Voting on top.gg')
        success = await asyncio.to_thread(topgg.vote, bot_id, client.token)
        if success:
            client.cooldown_vote = time.time() + 12 * 3600
            client.logger.info('Voted (next in 12 hours)')
        else:
            client.cooldown_vote = time.time() + 30 * 60
            client.logger.warning('Vote failed, retry later')