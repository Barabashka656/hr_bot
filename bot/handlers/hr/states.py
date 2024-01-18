from aiogram.fsm.state import StatesGroup, State

class HRState(StatesGroup):
    get_assistant_sys_prompt = State()
    gpt_dialogue = State()
