from typing import Any, Dict


class Message:

    def __init__(self, payload: Dict) -> None:
        self.payload = payload

    @property
    def op_type(self) -> str:
        return self.payload['t']

    @property
    def op_value(self) -> Any:
        return self.payload['v']

    @property
    def sheet_index(self) -> str:
        return self.payload['i']

    @property
    def is_cursor_move(self):
        return self.op_type == 'mv'
