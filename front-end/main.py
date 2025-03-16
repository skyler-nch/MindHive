import os
from dotenv import load_dotenv
from nicegui import ui
from layout.main_page import main_page_layout

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR,'.env'))

#TODO: typehints and structs all missing
#TODO: organize file/code structures

#TODO: P0!!!!! chat conversations are saved in server state, not client state
#fix by using app.storage.user instead, not storing it on server side
@ui.page('/')
async def main():
    dark = ui.dark_mode()
    dark.enable()
    main_page_layout()


if __name__ in {'__main__', '__mp_main__'}:
    ui.run()