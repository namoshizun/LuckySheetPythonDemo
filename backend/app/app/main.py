import json
from fastapi import FastAPI, Request
from .channel import routes as ws_routes, broadcast


app = FastAPI(
    routes=ws_routes, 
    on_startup=[broadcast.connect],
    on_shutdown=[broadcast.disconnect],
)


def get_init_sheetdata(encoded=False):
    celldata = [
        {
            "r":0,
            "c":0,
            "v": {
                "v": 11111,
                "m": "1",
                "ct": {
                    "fa": "General",
                    "t": "n"
                }
            }
        }
    ]

    sheet_data = {
        "name": "Cell",
        "index": "sheet_01",
        "order":  0,
        "status": 1,
        "column": 10,
        "celldata": celldata
    }

    if not encoded:
        return sheet_data
    
    return json.dumps(sheet_data).encode()


@app.post("/api/sheets")
async def get_sheets(request: Request):
    init_data = [get_init_sheetdata()]

    return json.dumps(init_data)


# @app.websocket('/ws/sheet-edit')
# async def sheet_edit_session(websocket: WebSocket, g: str):
#     await websocket.accept()
#     sess = LuckysheetSession(websocket, grid_key=g)

#     print(f'Established new session: {sess}')
#     await sess.send_connection_ok()

#     while True:
#         # Receive message
#         try:
#             pack = await websocket.receive_text()
#         except WebSocketDisconnect:
#             print('Client disconnected')
#             await sess.send_connection_close()
#             break

#         if pack == 'rub':  # heartbeat:
#             continue

#         unzip_bytes = zlib.decompress(pack.encode('iso-8859-1'), 16)
#         data = unquote(unzip_bytes.decode())

#         print('~' * 30)
#         print(data)

#         await websocket.send_json(get_init_sheetdata(encoded=False))
#         # await websocket.send_json()
#         # print('[luckys] ~' * 30)
