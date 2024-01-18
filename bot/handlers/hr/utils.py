import asyncio


class CustomSendAction:
    def __init__(self, bot, tg_id: int, state):
        self.bot = bot
        self.tg_id = tg_id
        self.loop_task = None
        self.running = False
        self.state_obj = state

    async def __aenter__(self):
        self.state = await self.state_obj.get_state()
        print(self.state)
        await self.state_obj.set_state("UserStates:no_more_messages")

        self.running = True
        self.loop_task = asyncio.create_task(self.typing_loop())

    async def typing_loop(self):
        while self.running:
            await self.bot.send_chat_action(chat_id=self.tg_id, action="record_voice")
            await asyncio.sleep(5)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.running = False
        if self.loop_task:
            try:
                await self.loop_task  # Await task to handle normal completion
            except asyncio.CancelledError:
                pass
        print(self.state)
        await self.state_obj.set_state(self.state)
        