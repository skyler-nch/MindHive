from uuid import uuid4
from nicegui import ui
import requests
import asyncio
from utils.request import get_request

messages = []
bot = str(uuid4())
bot_avatar = f'https://robohash.org/{bot}?bgset=bg2'
user = str(uuid4())
avatar = f'https://robohash.org/{user}?bgset=bg2'


async def backend(user_prompt):
    #backend has a limitation on providing full chat capabilities, so this bot is more akin to a QnA bot than a chatbot
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None,get_request,"/query",{"query":user_prompt})

    return response["response"]

@ui.refreshable
def chat_messages(own_id):
    for user_id, avatar, text in messages:
        with ui.column().classes("w-full items-stretch"):
            ui.chat_message(avatar=avatar, text=text, sent=user_id==own_id)

def chat_layout():
    async def send():
        loading =  ui.spinner(size="lg").classes("fixed-center")

        messages.append((user, avatar, text.value))
        user_prompt = text.value
        text.value = ''
        text.disable()
        chat_history.scroll_to(percent=1)
        chat_messages.refresh()

        response = await backend(user_prompt)
        messages.append((bot,bot_avatar,response))
        loading.set_visibility(False)
        text.enable()
        chat_history.scroll_to(percent=1)
        chat_messages.refresh()
        

    
    with ui.card().style("height:60%;width:80%;"):
        with ui.scroll_area().classes('w-full').style("width:100%;height:88%") as chat_history:
            chat_messages(user)

        with ui.row().classes('w-full absolute-bottom q-pa-sm'):
            with ui.avatar():
                ui.image(avatar)
            text = ui.input(placeholder='message').props('rounded outlined').classes('flex-grow').on('keydown.enter', send)