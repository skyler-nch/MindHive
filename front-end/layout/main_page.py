from nicegui import ui
from layout.chat_interface import chat_layout
from utils.request import get_request
from utils.structs import StoreContentStruct
from component.toggle_button import ToggleButton
from component.shop_detail import shop_details

#TODO: type hintings, models
#TODO: code logic is too convoluted, OOP would help here


def main_page_layout():
    shops_view_content = []
    markers = []
    catchments = []
    intersecting_shops = set(get_request("/getintersectingshops",{"distance":"5"}))

    def shops_update(response):
        shops_view_content.clear()
        for item in response:
            item["id"] = item["_id"] #its needed because pydantic cannot accept fields with _ as a prefix
            shops_view_content.append(StoreContentStruct(**item))
        return shops_view_content
        
    
    def get_all_shops():
        response = get_request("/getshops")
        return shops_update(response)
    
    def query_shops(query):
        response = get_request("/queryshops",{"query":query})
        return shops_update(response)

    def search():
        if text.value != "":
            response = query_shops(text.value)
        else:
            response = get_all_shops()
        

        if intersection_obj.state() == True:
            response = filter_intersecting(response)

        listing.refresh(response)
        map_markers.refresh(response)
        if catchment_obj.state() == True:
            #TODO: this is the code equivalent of turning it on and off, please have some dignity
            catchment(response)
        
    def filter_intersecting(list_of_shops):
        return [i for i in list_of_shops if i.id in intersecting_shops]
    
    def intersection():
        #TODO: bug where intersection of shops do not discount filtered shops\
        #can consider second pass negative filter that cross checks shops id
        if intersection_obj.state() == True:
            filtered_view = filter_intersecting(shops_view_content)
            listing.refresh(filtered_view)
            map_markers.refresh(filtered_view)
            catchment(filtered_view)
        else:
            listing.refresh(shops_view_content)
            map_markers.refresh(shops_view_content)
            catchment(shops_view_content)

    def catchment(shops=get_all_shops()):
        #TODO: add feature that allows for user to input catchment range
        state = catchment_obj.state()
        
        for item in catchments:
            item.run_method("remove")
        catchments.clear()
        if state == True:
            if intersection_obj.state() == True:
                shops = filter_intersecting(shops)
            for item in shops:
                #TODO: tweak opacity because the map is indiscernable because of stacking layers
                catchments.append(m.generic_layer(name = "circle",args=[(item.latitude,item.longitude),{"color":"red","radius":5000}]))
        

    @ui.refreshable
    def listing(shops):
        if len(shops) > 0:
            [shop_details(item,m) for item in shops]
        else:
            ui.label("sandwichless :(")

    @ui.refreshable
    def map_markers(shops):
        #delete old markers
        for item in markers:
            item.run_method("remove")

        #add new markers
        for item in shops:
            marker = m.marker(latlng=(item.latitude,item.longitude))
            markers.append(marker)

    with ui.column().classes("fullscreen"):
        
        with ui.splitter(horizontal=True,limits=[30,70]).style("width:100%;height:92%") as splitter:
            with splitter.before:
                m = ui.leaflet(center=(3.149835, 101.694423)).style("height:100%")

            with splitter.after:
                text = ui.input(placeholder="Search").props("rounded outlined").style("height:10%;width:100%;").on('keydown.enter', search)

                with ui.scroll_area().props("dense seperator").style("height:90%;width:100%;"):
                    listing(get_all_shops())
                    map_markers(get_all_shops())
                    
        with ui.dialog() as dialog:
            chat_layout()
        with ui.row().style("width:100%;justify-content:space-around"):
            ui.button('Chatbot', on_click=dialog.open).style("width:30%")
            catchment_obj = ToggleButton("Catchment").style("width:30%").on_click(catchment)
            intersection_obj = ToggleButton("Intersection").style("width:30%").on_click(intersection)
    