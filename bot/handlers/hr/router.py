from bot.handlers.hr.keyboards import HRCallback, TableCallback
# from bot.loader import bot
# from bot.handlers.chatgpt.services import ChatGPTService
# from bot.handlers.chatgpt.keyboards import new_dialogue_kb

from aiogram import F, Router
from aiogram import types
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext

from bot.handlers.hr.services import UserService
from bot.handlers.hr.states import HRState   


router = Router()

@router.callback_query(TableCallback.filter())
async def table_choice(
    callback: types.CallbackQuery,
    callback_data: TableCallback,
    state: FSMContext
):
    await callback.answer()
    await UserService.new_user(
        user_id=callback.from_user.id,
        table_number=int(callback_data.number),
        username=callback.from_user.username
    )
    await callback.message.answer(text='Напишите промпт')
    await state.set_state(HRState.get_assistant_sys_prompt)

@router.message(HRState.get_assistant_sys_prompt)
async def gpt_first(message: types.Message, state: FSMContext):
    messages = await state.get_data()
    messages = messages.get('first_gpt_data')
    messages = await ChatGPTService.get_openai_response(
        message.text, 
        messages,
        message.from_user.id
    )
    gpt_answer = messages[-1].get('content')
    await message.answer(text=gpt_answer)
    await state.update_data(first_gpt_data=messages)

@router.callback_query(HRCallback.filter())
async def create_hr(
    callback: types.CallbackQuery,
    callback_data: TableCallback,
    state: FSMContext
):
    