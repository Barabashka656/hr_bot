import io

from aiogram.filters import Command
from bot.handlers.hr.keyboards import HRCallback, TableCallback
# from bot.loader import bot
# from bot.handlers.chatgpt.services import ChatGPTService
# from bot.handlers.chatgpt.keyboards import new_dialogue_kb

from aiogram import F, Router
from aiogram import types
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext

from bot.handlers.hr.keyboards import create_hr_kb
from bot.handlers.hr.schemas import TableAssistant
from bot.handlers.hr.services import OpenAIService, UserService
from bot.handlers.hr.states import HRState
from bot.handlers.start.keyboards import tables_kb   
from bot.loader import bot

router = Router()

@router.message(Command("start_interview"))
@router.message(HRState.gpt_dialogue)
async def handle_interview(message: types.Message, state: FSMContext):
    reply_text = 'пожалуйста, подождите...'
    msg = await message.answer(reply_text) 
    await state.set_state(HRState.gpt_dialogue)
    await bot.send_chat_action(message.chat.id, 'record_voice')
    print(message.text, 'texttext')
    if message.voice:
        result: io.BytesIO = await bot.download(message.voice)
        users_answer = await OpenAIService.speech_to_text(result)
    else:
        users_answer = message.text

    fsm_data = await state.get_data()
    thread_id = fsm_data.get('thread_id')
    assistant_id = fsm_data.get('assistant_id')

    if users_answer == '/start_interview':
        thread_id = None
        users_answer = 'Начни интервью, задай кандидату минимум 5 коротких '\
            'вопросов по одному вопросу'\
            'после того как кандидат ответит оцени его ответ от 1 до 10/ '\
            'и продолжай задавать вопросы '\
            'отвечай и задавай короткие вопросы так как мы будем озвучивать их через (TTS) '

    

    user_id = message.from_user.id
    if not assistant_id:
        assistant_id = await UserService._get_assistantid_by_userid(user_id)
    if not assistant_id:
        reply_text = 'сначала выберете стол'
        table_count = await UserService.table_count()
        return await message.answer(text=reply_text, reply_markup=tables_kb(table_count))

    response, thread_id = await OpenAIService.get_assistant_response(
        thread_id=thread_id,
        assistant_id=assistant_id,
        user_input=users_answer,
        user_id=user_id
    )
    bytes_voice = await OpenAIService.text_to_speech(response)
    await msg.delete()
    await message.answer_voice(
        types.BufferedInputFile(
            bytes_voice,
            filename="voice.ogg"
        )
    )
    await state.update_data(thread_id=thread_id)


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
    await callback.message.answer(text='задайте пропт текстом или голосом')
    await state.set_state(HRState.get_assistant_sys_prompt)

@router.message(HRState.get_assistant_sys_prompt)
async def get_prompt(message: types.Message, state: FSMContext):
    if message.voice:
        result: io.BytesIO = await bot.download(message.voice)
        users_answer = await OpenAIService.speech_to_text(result)
    else:
        users_answer = message.text
    await UserService.add_prompt_to_db(
        user_id=message.from_user.id, 
        prompt=users_answer
    )
    reply_text = 'вы можете дополнять промпт, '\
                'когда промпт будет готов, нажмите на кнопку "создать HR"'
    await message.answer(text=reply_text, reply_markup=create_hr_kb)

@router.callback_query(HRCallback.filter())
async def create_hr(
    callback: types.CallbackQuery,
    callback_data: TableCallback,
    state: FSMContext
):
    assistant_id = await OpenAIService.create_assistant(callback)
    if not isinstance(assistant_id, str):
        print('1234err')
        reply_text = 'ваш стол уже создал hr бота'
        print(reply_text)
        return await callback.answer(text=reply_text)
    
    users = await UserService.get_users_at_table_by_userid(callback.from_user.id)
    for user in users:
        reply_text = 'Hr создан, нажмите\n/start_interview'
        await bot.send_message(chat_id=user, text=reply_text)
    await callback.answer()

