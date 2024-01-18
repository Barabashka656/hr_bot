from aiogram.fsm.state import StatesGroup, State

class HRState(StatesGroup):
    get_assistant_sys_prompt = State()
    second_gpt_data = State()
    third_gpt_data = State()
