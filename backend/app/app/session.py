import contextlib
import json
import zlib
from datetime import datetime
from typing import Any, AsyncGenerator
from functools import wraps
from urllib.parse import unquote
from starlette.websockets import WebSocket, WebSocketDisconnect

from .message import Message


class StatusCode:
    ok = "0"
    err = "1"


class ReplyType:
    recv_conn = "0"
    unicast = "1"
    broadcast = "2"
    notify_selection = "3"
    close_conn = "999"


def stringify(fun):
    @wraps(fun)
    def decor(*args, **kwargs):
        ret = fun(*args, **kwargs)
        if isinstance(ret, dict):
            return json.dumps(ret)
        return ret
    return decor


class LuckysheetSession:

    def __init__(self, ws: WebSocket, grid_key: str) -> None:
        self.id = str(datetime.now().microsecond)
        self.grid_key = grid_key
        self.username = f'testuser-{self.id}'
        self.connect_time = datetime.now()
        self.websocket: WebSocket = ws

    @property
    def channel(self):
        return f'sheet-???/grid-{self.grid_key}'  # TODO: allow switching between sheets

    def __get_metadata(self):
        # Doc: https://mengshukeji.github.io/LuckysheetDocs/zh/guide/operate.html#%E5%90%8E%E7%AB%AF%E8%BF%94%E5%9B%9E%E6%A0%BC%E5%BC%8F
        return {
            'id': self.id,
            'username': self.username,
            'returnMessage': 'success'
        }

    @stringify
    def get_connection_ok_message(self):
        return {
            'message': '连接成功',
            'status': StatusCode.ok,
            'type': ReplyType.recv_conn,
        }

    @stringify
    def get_connection_close_message(self):
        return dict(
            **self.__get_metadata(),
            **{
                'message': '用户退出',
                'type': ReplyType.close_conn,
            }
        )

    @stringify
    def get_broadcast_message(self, data: Any, **kwargs):
        payload = dict(
            **self.__get_metadata(),
            **{
                'status': StatusCode.ok,
                'data': json.dumps(data),
                'type': ReplyType.broadcast
            }
        )
        payload.update(kwargs)
        return payload

    async def iter_message(self) -> AsyncGenerator[Message, None]:
        with contextlib.suppress(WebSocketDisconnect):
            while True:
                pack = await self.websocket.receive_text()
                if pack == 'rub':  # heartbeat
                    continue

                unzip_bytes = zlib.decompress(pack.encode('iso-8859-1'), 16)
                data_str = unquote(unzip_bytes.decode())
                yield Message(json.loads(data_str))

    def __str__(self) -> str:
        return f'uuid {self.id}, connected at {self.connect_time}'
