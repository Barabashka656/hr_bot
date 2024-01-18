import asyncio
from bot.handlers.hr.dao import TableAssistantDAO
from bot.utils.database import async_session_maker
import os
from flask import Flask, render_template
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

app = Flask(__name__)


# Helper function to run async database operations
def get_table_assistants_sync():
    async def run_db():
        async with async_session_maker() as session:
            objects = await TableAssistantDAO.find_all(session=session)
        return objects
    
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # If there's no running loop
        return asyncio.run(run_db())
    
    if loop.is_running():
        # Create a new event loop for async tasks when the current loop is running
        return asyncio.run(run_db())
    else:
        # Run in the existing event loop if not running
        return loop.run_until_complete(run_db())


@app.route('/')
def get_prompts():
    objects = get_table_assistants_sync()
    return render_template('get_sys_prompts.html', objects=objects)


if __name__ == '__main__':
    # Uncomment one of these depending on your deployment setup
    # app.run(host='0.0.0.0')
    port = os.getenv('PORT', 5000)  # Default to 5000 if PORT is not set
    app.run(host='0.0.0.0', port=port)
