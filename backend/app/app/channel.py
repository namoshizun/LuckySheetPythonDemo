import typing
import functools
import anyio
import os

from starlette.websockets import WebSocket
from starlette.routing import WebSocketRoute
from broadcaster import Broadcast
from .session import LuckysheetSession, ReplyType


_env = os.environ

if password := _env.get('REDIS_PASSWORD'):
    redis_url = f"redis://:{password}@{_env['REDIS_HOST']}:{_env['REDIS_PORT']}"
else:
    redis_url = f"redis://{_env['REDIS_HOST']}:{_env['REDIS_PORT']}"

broadcast = Broadcast(redis_url)


async def __run_until_first_complete(*args: typing.Tuple[typing.Callable, dict]) -> None:

    async with anyio.create_task_group() as task_group:

        async def _run(func: typing.Callable[[], typing.Coroutine]) -> None:
            await func()
            task_group.cancel_scope.cancel()

        for func, kwargs in args:
            task_group.start_soon(_run, functools.partial(func, **kwargs))


async def sheet_edit_ws(websocket: WebSocket):
    await websocket.accept()

    grid_key = websocket.query_params['g']
    session = LuckysheetSession(websocket, grid_key=grid_key)
    await websocket.send_text(session.get_connection_ok_message())

    await __run_until_first_complete(
        (_message_handler, {"session": session}),
        (_message_broadcaster, {"session": session}),
    )


async def _message_handler(session: LuckysheetSession):
    broadcast_fun = functools.partial(broadcast.publish, channel=session.channel)
    last_received = None

    async for message in session.iter_message():
        if (data := message.payload) == last_received:
            continue

        if message.is_cursor_move:
            reply_type = ReplyType.notify_selection
            message = session.get_broadcast_message(data, type=reply_type)
            await broadcast_fun(message=message)
        else:
            await broadcast_fun(message=session.get_broadcast_message(data))

        last_received = data

    # Disconnected
    await broadcast_fun(message=session.get_connection_close_message())


async def _message_broadcaster(session: LuckysheetSession):
    async with broadcast.subscribe(channel=session.channel) as subscriber:
        async for event in subscriber:
            message = event.message

            if session.id not in message:
                await session.websocket.send_text(message)


routes = [
    WebSocketRoute("/ws/sheet-edit", sheet_edit_ws, name="sheet-edit-session"),
]
