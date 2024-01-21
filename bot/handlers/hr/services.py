import asyncio
import datetime
from io import BytesIO
import json

from aiogram import types
from bot.handlers.hr.models import AssistantModel, UserModel

from bot.loader import openai_client
from bot.handlers.hr.dao import AssistantDAO, UserDAO, ThreadDAO
from bot.handlers.hr.schemas import User, Assistant, ThreadSchema
from bot.utils.database import async_session_maker

from openai.types.beta.threads import Run, ThreadMessage
from openai.types.beta.thread import Thread


class UserService:
    @staticmethod
    async def new_user(user_id: int, username: str):
        async with async_session_maker() as session:
            user: User = await UserDAO.find_one_or_none(
                session,
                UserModel.user_id == user_id
            )
            if not user:
                await UserDAO.add(
                    session,
                    obj_in=User(
                        user_id=user_id,
                        username=username
                    )
                )
                await session.commit()


    @classmethod
    async def get_assistant_id(cls, user_id: int) -> str | None:
        async with async_session_maker() as session:

            assistant: Assistant = await AssistantDAO.find_one_or_none(
                session,
                AssistantModel.user_id == user_id
            )
            if assistant:
                return assistant.assistant_id
        
    @staticmethod
    async def new_thread(assistant_id: str, thread_id: str, created_at: datetime.datetime):
        async with async_session_maker() as session:
            await ThreadDAO.add(
                session,
                obj_in=ThreadSchema(
                    assistant_id=assistant_id,
                    thread_id=thread_id,
                    created_at=created_at
                )
            )
            return await session.commit()
        
    @staticmethod
    async def check_assist_count(user_id: int) -> int:
        async with async_session_maker() as session:
            return await AssistantDAO.count(
                session,
                AssistantModel.user_id == user_id
            )
        
    @staticmethod
    async def get_assistants(user_id: int) -> list[Assistant]:
        async with async_session_maker() as session:
            return await AssistantDAO.find_all(
                session,
                AssistantModel.user_id == user_id
            )


class OpenAIService:
    hr_function = [
        {
            "type": "function",
            "function" : {
                "name": "end_interview",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "mark": {
                            "type": "number",
                            "description": "конечная оценка кандидата (от 1 до 10), "\
                                "расчитаная на основе предыдущих оценок"
                        },
                        "approve": {
                            "type": "boolean",
                            "description": "принимаешь ли ты как hr данного кандидата"
                        },
                    },
                    "required": [
                        "mark",
                        "approve"
                    ]
                },
                "description": "окончательное решение hr менеджера  "\
                    "о приеме кандидата на работу, функция вызывается "\
                    "только тогда, когда hr готов озвучить данное решение " \
                    "и только после того, как hr задаст несколько вопросов "
            }
        }
    ]

    @classmethod
    async def create_assistant(cls, user_id: int, prompt) -> str:
        'returns assistant id'

        prompt+="\n\nОтвечай и задавай короткие вопросы, так как мы будем озвучивать их через (TTS). "\
               "За раз задавай только 1 вопрос. Ни в коем случае не задавай 2 вопроса подряд в 1 сообщении. "\
               "Все цифры и числа пиши только текстом. Если хочешь написать 1/10, пиши ОДИН ИЗ ДЕСЯТИ. "\
               "В ответах не должно быть ни одного символа цифры"

        async with async_session_maker() as session:
            assistant = await openai_client.beta.assistants.create(
                        name="Hr менеджер",
                        instructions=prompt,
                        model="gpt-4-1106-preview",
                        tools=cls.hr_function
            )
            await AssistantDAO.add(
                session,
                obj_in=Assistant(
                    assistant_id=assistant.id,
                    user_id=user_id,
                    sys_prompt=prompt
                )
            )
            await session.commit()
            return assistant.id
    
    @staticmethod
    async def text_to_speech(input_text: str) -> bytes:
        response = await openai_client.audio.speech.create(
            model="tts-1-hd",
            voice="alloy",
            input=input_text,
            response_format='opus'
        )
        return response.content

    @staticmethod
    async def speech_to_text(bytes_audio: BytesIO) -> str:
        bytes_audio.name = "voice.ogg"
        return await openai_client.audio.transcriptions.create(
            model="whisper-1",
            response_format='text',
            file=bytes_audio
        )
    
    @staticmethod
    async def _submit_message(
        thread_id: str,
        user_message: str,
        assistant_id: str
    ) -> Run:
        await openai_client.beta.threads.messages.create(
            thread_id=thread_id, role="user", content=user_message
        )
        return await openai_client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
        )
    
    @staticmethod
    async def _get_response(thread_id: str):
        return await \
            openai_client.beta.threads.messages.list(thread_id=thread_id)

    @classmethod
    async def _create_thread_and_run(cls, user_input, assistant_id) -> tuple[str, Run]:
        
        thread: Thread = await openai_client.beta.threads.create()
        await UserService.new_thread(assistant_id, thread.id, thread.created_at)
        run = await cls._submit_message(thread.id, user_input, assistant_id)
        
        return thread.id, run
    

    @staticmethod
    async def end_interview(argumets: str) -> str:
        argumets = json.loads(argumets)
        if argumets.get('approve'):
            hr_answer = 'Вы прошли'
        else:
            hr_answer = 'Вы не прошли'
        
        return hr_answer + f' собеседование, ваша оценка: ' + str(argumets.get('mark'))
    
    @classmethod
    async def _retrieve_run(cls, run, thread_id):
        while run.status == "queued" or run.status == "in_progress":
            await asyncio.sleep(0.3)
            run = await openai_client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id,
            )
            
            if run.status == "requires_action":
                hr_answer = await cls.end_interview(run.required_action.submit_tool_outputs.tool_calls[0].function.arguments)
                required_action = await openai_client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=[
                        {
                            "tool_call_id": run.required_action.submit_tool_outputs.tool_calls[0].id,
                            "output": 'диалог закончен'
                        }
                    ]
                )
                return hr_answer
    
    @classmethod
    async def get_assistant_response(
        cls, 
        thread_id: str | None, 
        assistant_id: str | None,
        user_input: str
    ) -> tuple[str, str, bool]:
        if thread_id:
            run = await cls._submit_message(thread_id, user_input, assistant_id)
        else:
            thread_id, run = await cls._create_thread_and_run(
                user_input=user_input,
                assistant_id=assistant_id
            )

        answer = await cls._retrieve_run(run, thread_id)
        if answer:
            return answer, thread_id, True
        
        response = await cls._get_response(thread_id)
        message: ThreadMessage = response.data[0]
        return message.content[0].text.value, thread_id, False
