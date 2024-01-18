import asyncio
import datetime
from io import BytesIO
import json

from aiogram import types
from bot.handlers.hr.models import TableAssistantModel, TableModel

from bot.loader import openai_client
from bot.handlers.hr.dao import TableAssistantDAO, TableDAO, ThreadDAO, UtilDAO
from bot.handlers.hr.schemas import Table, TableAssistant, ThreadSchema, UtilSchema
from bot.utils.database import async_session_maker

from openai.types.beta.threads import Run, ThreadMessage
from openai.types.beta.thread import Thread

class UserService:
    @staticmethod
    async def new_user(user_id: int, table_number: int, username: str):
        async with async_session_maker() as session:
            print('new_one')
            db_user = await TableDAO.add(
                session,
                obj_in=Table(
                    user_id=user_id,
                    table_number=table_number,
                    username=username
                )
            )
            print(db_user)
            await session.commit()
        return db_user
    
    @staticmethod
    async def get_users_at_table_by_userid(user_id: int) -> list[int]: # TODO(??)
        async with async_session_maker() as session:
            table: Table = await TableDAO.find_one_or_none(
                session,
                TableModel.user_id == user_id
            )
            users_db: list[Table] = await TableDAO.find_all(
                session,
                TableModel.table_number == table.table_number
            )
            return [user.user_id for user in users_db]

    @staticmethod
    async def _get_table_num_by_userid(user_id: int) -> int | None:
        async with async_session_maker() as session:
            table: Table = await TableDAO.find_one_or_none(
                session,
                TableModel.user_id == user_id
            )
            if not table:
                return None
            return table.table_number
        
    @classmethod
    async def _get_assistantid_by_userid(cls, user_id: int) -> str | None:
        async with async_session_maker() as session:
            table_number = await cls._get_table_num_by_userid(user_id)
            if not table_number:
                return None

            table_assistant: TableAssistant = await TableAssistantDAO.find_one_or_none(
                session,
                TableAssistantModel.table_number == table_number
            )
            return table_assistant.assistant_id
        
    @classmethod
    async def add_prompt_to_db(cls, user_id: int, prompt: str):
        async with async_session_maker() as session:
            table_number = await cls._get_table_num_by_userid(user_id)
            table_assistant: TableAssistant = await TableAssistantDAO.find_one_or_none(
                session,
                TableAssistantModel.table_number == table_number
            )
            if not table_assistant:
                await TableAssistantDAO.add(
                    session,
                    obj_in=TableAssistant(
                        table_number=table_number,
                        sys_prompt=prompt
                    )
                )
            else:
                table_assistant.sys_prompt+=f'\{prompt}'

            return await session.commit()
        
    @classmethod
    async def get_table_assistant_by_user_id(cls, user_id: int):
        async with async_session_maker() as session:
            table_number = await cls._get_table_num_by_userid(user_id)
            table_assistant: TableAssistant = await TableAssistantDAO.find_one_or_none(
                session,
                TableAssistantModel.table_number == table_number
            )
            return table_assistant
        
    @staticmethod
    async def new_thread(user_id: int, thread_id: str, created_at: datetime.datetime):
        async with async_session_maker() as session:
            print('add2')
            await ThreadDAO.add(
                session,
                obj_in=ThreadSchema(
                    user_id=user_id,
                    thread_id=thread_id,
                    created_at=created_at
                )
            )
            return await session.commit()
        
    @staticmethod
    async def table_count() -> int:
        async with async_session_maker() as session:
            util: UtilSchema = await UtilDAO.find_one_or_none(
                session,
            )
            return util.tables_count

    @classmethod   
    async def set_table_count_default(cls, count: int):
        async with async_session_maker() as session:
            table_count = await cls.table_count()
            if table_count:
                return
            await UtilDAO.add(
                session,
                obj_in=UtilSchema(
                    tables_count=count
                )
            )
            return await session.commit()

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
    async def create_assistant(cls, callback: types.CallbackQuery) -> str:
        'returns assistant id'
    
        async with async_session_maker() as session:
            # table_assistant: TableAssistant = await \
            #     UserService.get_table_assistant_by_user_id(callback.from_user.id)

            table_number = await UserService._get_table_num_by_userid(callback.from_user.id)
            table_assistant: TableAssistant = await TableAssistantDAO.find_one_or_none(
                session,
                TableAssistantModel.table_number == table_number
            )
            if not table_assistant.sys_prompt:
                reply_text = 'у вас не задан промпт'
                return await callback.answer(text=reply_text)
            if table_assistant.assistant_id:
                
                reply_text = 'ваш стол уже создал hr бота'
                print(reply_text)
                return await callback.answer(text=reply_text)

            assistant = await openai_client.beta.assistants.create(
                        name="Hr менеджер",
                        instructions=table_assistant.sys_prompt,
                        model="gpt-4-1106-preview",
                        tools=cls.hr_function
            )
            assistant
            print(assistant.id)
            table_assistant.assistant_id = assistant.id
            print(table_assistant)
            print(table_assistant.assistant_id)
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
    async def _create_thread_and_run(cls, user_input, assistant_id, user_id) -> tuple[str, Run]:
        
        thread: Thread = await openai_client.beta.threads.create()
        print('add1')
        await UserService.new_thread(user_id, thread.id, thread.created_at)
        run = await cls._submit_message(thread.id, user_input, assistant_id)
        
        return thread.id, run
    

    @staticmethod
    async def end_interview(argumets: dict[int, bool]) -> str:
        argumets = json.loads(argumets)
        if argumets.get('approve'):
            hr_answer = 'вы прошли'
        else:
            hr_answer = 'вы не прошли'
        
        return hr_answer + f' собеседование, ваш оценка: ' + str(argumets.get('mark'))
    
    @classmethod
    async def _retrieve_run(cls, run, thread_id):
        while run.status == "queued" or run.status == "in_progress":
            await asyncio.sleep(0.3)
            run = await openai_client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id,
            )
            
            if run.status == "requires_action":
                print(run.required_action)
                hr_answer = await cls.end_interview(run.required_action.submit_tool_outputs.tool_calls[0].function.arguments[0])
                required_action = await openai_client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=[
                        {
                            "tool_call_id": run.required_action.submit_tool_outputs.tool_calls[0].id,
                            "output": hr_answer
                        }
                    ]
                )
                return hr_answer
    
    @classmethod
    async def get_assistant_response(
        cls, 
        thread_id: str | None, 
        assistant_id: str | None,
        user_input: str,
        user_id: int | None
    ) -> tuple[str, str]:
        if thread_id:
            run = await cls._submit_message(thread_id, user_input, assistant_id)
        else:
            print('add3')
            thread_id, run = await cls._create_thread_and_run(
                user_input=user_input,
                assistant_id=assistant_id,
                user_id=user_id
            )

        answer = await cls._retrieve_run(run, thread_id)
        if answer:
            return answer
        response = await cls._get_response(thread_id)
        message: ThreadMessage = response.data[0]
        return message.content[0].text.value, thread_id
