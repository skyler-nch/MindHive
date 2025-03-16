from nicegui import ui
import time
def shop_details(payload,map):
    def focus_shop():
        map.run_map_method("setView",(payload.latitude,payload.longitude),18)
        
    with ui.card().style("width:100%"):
        ui.label(payload.name)
        ui.label(payload.address)
        for times in payload.opening_times:
            ui.label(times)
        with ui.row().classes().style("width:100%"):
            ui.button("Show",on_click=focus_shop)
            ui.button("Waze",on_click=lambda: ui.navigate.to(payload.waze_link,new_tab=True))
            ui.button("Maps",on_click=lambda: ui.navigate.to(payload.google_map_link,new_tab=True))
