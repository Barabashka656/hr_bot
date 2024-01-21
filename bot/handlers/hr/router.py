import io

from aiogram.filters import Command
from bot.data.config import MAX_ASSISTANTS_PER_USER
from bot.handlers.hr.keyboards import ChooseHRCallback, HRCallback, assistants_kb


from aiogram import F, Router
from aiogram import types
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext

from bot.handlers.hr.keyboards import create_hr_kb
from bot.handlers.hr.schemas import Assistant
from bot.handlers.hr.services import OpenAIService, UserService
from bot.handlers.hr.states import HRState
from bot.loader import bot
from bot.handlers.hr.utils import CustomSendAction

router = Router()


@router.message(Command("start_interview"))
@router.message(HRState.gpt_dialogue)
async def handle_interview(message: types.Message, state: FSMContext):
    fsm_data = await state.get_data()
    thread_id = fsm_data.get('thread_id')
    assistant_id = fsm_data.get('assistant_id')
        
    if not assistant_id:
        reply_text = "выберите ассистента /choose_assistant\n"\
                     "или создайте нового /create_assistant"
        await state.clear()
        return await message.answer(text=reply_text)
    
    async with CustomSendAction(bot=bot, tg_id=message.from_user.id, state=state):
        if message.voice:
            result: io.BytesIO = await bot.download(message.voice)
            users_answer = await OpenAIService.speech_to_text(result)
        else:
            users_answer = message.text
        
        
        reply_text = 'пожалуйста, подождите...'
        msg = await message.answer(reply_text)
        await state.set_state(HRState.gpt_dialogue)
        
        if users_answer == '/start_interview':
            thread_id = None
            users_answer = 'Добрый вечер, я кандидат на вакансию. Хочу начать интервью'

        response, thread_id, is_finished = await OpenAIService.get_assistant_response(
            thread_id=thread_id,
            assistant_id=assistant_id,
            user_input=users_answer
        )
        
    if is_finished:
        await msg.delete()
        await message.answer(response)
        reply_text = "Если у Вас остались вопросы по интервью, задайте их. "\
                     "Если Вы хотите начать интервью заново, нажмите /start_interview\n"\
                     "для того, чтобы создать нового ассистента, нажмите /create_assistant\n"\
                     "для того, чтобы создать нового ассистента, нажмите /choose_assistant"
        return await message.answer(text=reply_text)
        
    bytes_voice = await OpenAIService.text_to_speech(response)
    await msg.delete()
    await message.answer_voice(
        types.BufferedInputFile(
            bytes_voice,
            filename="voice.ogg"
        )
    )
    await state.update_data(thread_id=thread_id)


@router.message(Command('create_assistant'))
async def create_assistant(message: types.Message, state: FSMContext):
    # await message.edit_reply_markup(reply_markup=None)
    assistants_count = await UserService.check_assist_count(message.from_user.id)

    if assistants_count >= MAX_ASSISTANTS_PER_USER:
        reply_text = "нельзя создавать более 3 ассистентов"
        return await message.answer(reply_text)
    
    reply_text = 'Задайте промпт текстом или голосом.'\
                 'Рекомендуем кратко описать:\n\n'\
                 '1. Характер HR\n'\
                 '2. Должность, на которую нанимаете\n'\
                 '3. Компанию и ее ценности\n'\
                 '4. На что обратить внимание\n'\
                 'и любые другие Ваши идеи'
    await message.answer(text=reply_text)
    await state.set_state(HRState.get_assistant_sys_prompt)

@router.message(Command('choose_assistant'))
async def choose_assistant(message: types.Message, state: FSMContext):
    await state.clear()
    assistants = await UserService.get_assistants(message.from_user.id)
    if not assistants:
        reply_text = "похоже, у вас пока нет ассистентов, нажмите\n/create_assistant"
        return await message.answer(text=reply_text)
    for idx, assistant in enumerate(assistants):
        reply_text = f"hr менеджер №{idx+1}\n" + assistant.sys_prompt
        await message.answer(text=reply_text)

    reply_text = 'выберите ассистента'
    await message.answer(text=reply_text, reply_markup=assistants_kb(assistants))

@router.message(HRState.get_assistant_sys_prompt)
async def get_prompt(message: types.Message, state: FSMContext):
    if message.voice:
        result: io.BytesIO = await bot.download(message.voice)
        users_answer = await OpenAIService.speech_to_text(result)
    else:
        users_answer = message.text

    reply_text = 'Вы можете дополнять промпт. ' \
                 'Когда промпт будет готов, нажмите на кнопку "Создать HR". '
    await message.answer(text=reply_text, reply_markup=create_hr_kb)

    fsm_data = await state.get_data()
    prompt = fsm_data.get('prompt')
    if prompt:
        await state.update_data(prompt=prompt+f'\n{users_answer}')
    else:
        await state.update_data(prompt=users_answer)

@router.callback_query(ChooseHRCallback.filter())
async def choose_hr(
        callback: types.CallbackQuery,
        callback_data: ChooseHRCallback,
        state: FSMContext
):
    await callback.answer()
    await state.update_data(assistant_id=callback_data.assistant_id)

    reply_text = 'HR выбран, нажмите\n/start_interview'
    await callback.message.answer(text=reply_text)

@router.callback_query(HRCallback.filter())
async def create_hr(
        callback: types.CallbackQuery,
        callback_data: HRCallback,
        state: FSMContext
):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    
    fsm_data = await state.get_data()
    prompt = fsm_data.get('prompt')
    print(prompt, '1')
    if not prompt:
        reply_text = 'сначала задайте промпт'
        return await callback.answer(text=reply_text)
    
    assistant_id = await OpenAIService.create_assistant(
        user_id=callback.from_user.id,
        prompt=prompt
    )
    
    await state.update_data(assistant_id=assistant_id)

    reply_text = 'HR создан, нажмите\n/start_interview'
    await callback.message.answer(text=reply_text)
