import asyncio
import datetime
import random
import time

from modules.bots.owo.checklist import Checklist
from modules.bots.owo.quest import Quest
from modules.bots.owo.vote import Vote
from modules.bots.owo.daily import Daily
from modules.bots.owo.huntbot import Huntbot
from modules.bots.owo.spam import Spam
from modules.bots.owo.gem import Gem
from modules.bots.owo.gamble import Gamble
from modules.bots.owo.channel import Channel


class TaskManager:
    def __init__(self, client):
        self.client = client
        self._tasks = []
        self._running = False

    def _any_spam(self):
        spam = self.client.config['spam']
        return spam['hunt'] or spam['battle'] or spam['owo/uwu']

    def should_checklist(self):
        return self.client.config['checklist']

    def should_quest(self):
        return self.client.config['quest'] or self.client.config['checklist']

    def should_vote(self):
        return self.client.config['vote'] or self.client.config['checklist']

    def should_daily(self):
        return self.client.config['daily'] or self.client.config['checklist']

    def should_huntbot(self):
        return self.client.config['huntbot']

    def should_spam(self):
        return self.client.config['checklist'] or self.client.config['quest'] or self._any_spam()

    def should_gamble(self):
        gamble = self.client.config['gamble']
        return (self.client.config['quest']
                or gamble['lottery']['mode'] or gamble['slot']['mode']
                or gamble['coinflip']['mode'] or gamble['blackjack']['mode']
                or gamble['highlow']['mode'])

    def should_glitch(self):
        return self.client.config['gem']['glitch']

    async def start(self):
        if self._running:
            return
        self._running = True

        if (self.should_checklist() or self.should_quest()) and self.client.interaction:
            self.client.interaction.ensure('cookie')

        todo = []
        if self.client.config['channels_id'] and len(self.client.config['channels_id']) > 1:
            todo.append((self._loop_channel, 0))
        if self.should_checklist():
            todo.append((self._loop_checklist, 0))
        if self.should_quest():
            todo.append((self._loop_quest, 3))
        if self.should_vote():
            todo.append((self._loop_vote, 0))
        if self.should_daily():
            todo.append((self._loop_daily, 0))
        if self.should_huntbot():
            todo.append((self._loop_huntbot, 8))
        if self.should_spam():
            todo.append((self._loop_spam, 10))
        if self.should_glitch():
            todo.append((self._loop_glitch, 5))
        if self.should_gamble():
            todo.append((self._loop_gamble, 0))
        if self.client.config['check_status']:
            todo.append((self._loop_offline_check, 0))

        for coro_func, delay in todo:
            if delay:
                await asyncio.sleep(delay)
            self._tasks.append(asyncio.create_task(coro_func()))

        self.client.logger.info('All tasks started')

    def create_background(self, coro, name=None):
        task = asyncio.create_task(coro, name=name)
        self._tasks.append(task)
        return task

    async def stop(self):
        self._running = False
        for task in self._tasks:
            if not task.done():
                task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks = []
        self.client.logger.info('All tasks stopped')

    async def _loop_channel(self):
        try:
            while self._running:
                channels = self.client.config['channels_id']
                if self.client.can_run() and len(channels) > 1:
                    changing_channel = self.client.config['changing_channel']
                    cooldown = random.randint(int(changing_channel['after_elapsed_time']['min']),
                                              int(changing_channel['after_elapsed_time']['max']))
                    self.client.logger.info(f'Next channel change in {cooldown}s')
                    await asyncio.sleep(cooldown)
                    try:
                        await Channel.change_channel(self.client)
                    except Exception:
                        self.client.logger.exception('Channel change error')
                else:
                    await asyncio.sleep(30)
        except asyncio.CancelledError:
            pass

    async def _loop_checklist(self):
        try:
            while self._running:
                if self.client.can_run() and self.should_checklist():
                    ok = True
                    try:
                        ok = await Checklist.check(self.client)
                    except Exception:
                        self.client.logger.exception('Checklist error')
                        ok = False
                    wait = Checklist.schedule(self.client) if ok else random.randint(60, 120)
                    self.client.daily_checklist_cooldown = time.time() + wait
                    self.client.weekly_checklist_cooldown = time.time() + wait
                    self.client.logger.info(f'Next checklist check in {datetime.timedelta(seconds=wait)}')
                    await asyncio.sleep(wait)
                else:
                    await asyncio.sleep(random.randint(30, 60))
        except asyncio.CancelledError:
            pass

    async def _loop_quest(self):
        try:
            while self._running:
                if self.client.can_run() and self.should_quest():
                    try:
                        await Quest.do_quest(self.client)
                    except Exception:
                        self.client.logger.exception('Quest error')
                await asyncio.sleep(random.randint(30, 60))
        except asyncio.CancelledError:
            pass

    async def _loop_vote(self):
        try:
            while self._running:
                if self.client.can_run() and self.should_vote():
                    try:
                        await Vote.vote(self.client)
                    except Exception:
                        self.client.logger.exception('Vote error')
                    remain = self.client.cooldown_vote - time.time()
                    await asyncio.sleep(min(remain, 300) if remain > 0 else random.randint(30, 60))
                else:
                    await asyncio.sleep(random.randint(30, 60))
        except asyncio.CancelledError:
            pass

    async def _loop_daily(self):
        try:
            while self._running:
                if self.client.can_run() and self.should_daily():
                    try:
                        await Daily.claim(self.client)
                    except Exception:
                        self.client.logger.exception('Daily error')
                await asyncio.sleep(random.randint(30, 60))
        except asyncio.CancelledError:
            pass

    async def _loop_huntbot(self):
        try:
            while self._running:
                if self.client.can_run() and self.should_huntbot():
                    try:
                        await Huntbot.claim_submit(self.client)
                    except Exception:
                        self.client.logger.exception('Huntbot error')
                await asyncio.sleep(random.randint(30, 60))
        except asyncio.CancelledError:
            pass

    async def _loop_spam(self):
        try:
            while self._running:
                if self.client.can_run():
                    try:
                        await Spam.spam_cycle(self.client)
                    except Exception:
                        self.client.logger.exception('Spam error')
                    spam = self.client.config['spam']
                    await asyncio.sleep(random.randint(int(spam['cooldown']['min']),
                                                       int(spam['cooldown']['max'])))
                else:
                    await asyncio.sleep(random.randint(30, 60))
        except asyncio.CancelledError:
            pass

    async def _loop_glitch(self):
        try:
            while self._running:
                if self.client.can_run() and self.should_glitch():
                    try:
                        await Gem.check_glitch(self.client)
                    except Exception:
                        self.client.logger.exception('Glitch error')
                await asyncio.sleep(random.randint(600, 1200))
        except asyncio.CancelledError:
            pass

    async def _loop_gamble(self):
        try:
            while self._running:
                if self.client.can_run():
                    gamble = self.client.config['gamble']
                    try:
                        await Gamble.gamble_cycle(self.client)
                    except Exception:
                        self.client.logger.exception('Gamble error')
                    await asyncio.sleep(random.randint(int(gamble['cooldown']['min']),
                                                       int(gamble['cooldown']['max'])))
                else:
                    await asyncio.sleep(random.randint(30, 60))
        except asyncio.CancelledError:
            pass

    async def _loop_offline_check(self):
        try:
            while self._running:
                if self.client.can_run():
                    if time.time() - self.client.last_owo_message_time > 60:
                        try:
                            await self._check_owo_alive()
                        except Exception:
                            self.client.logger.exception('Offline check error')
                await asyncio.sleep(random.randint(30, 60))
        except asyncio.CancelledError:
            pass

    async def _check_owo_alive(self):
        if not self.client.current_channel:
            return

        action = random.choice(self.client.owo_actions)
        await self.client.current_channel.send(f'{self.client.prefix}{action} {self.client.owo_bot.mention}')
        self.client.logger.info(f'Offline check: sent {self.client.prefix}{action} {self.client.owo_bot.mention}')

        try:
            await self.client.wait_for(
                'message',
                check=lambda m: m.author.id == self.client.owo_bot.id,
                timeout=5,
            )
            self.client.logger.info('OWO bot is online')
        except asyncio.TimeoutError:
            self.client.logger.warning('OWO bot is offline')
            wait = random.randint(300, 600)
            self.client.logger.info(f'Pausing for {wait}s')
            self.client.paused = True
            await asyncio.sleep(wait)
            self.client.paused = False
            self.client.logger.info('Resuming after offline pause')