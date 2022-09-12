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
            "r": 0,
            "c": 0,
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
    return json.dumps([get_init_sheetdata()])

