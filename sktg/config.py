import json
import pathlib

_token_file = pathlib.Path("config") / "tokens.json"
_tokens: dict[str, str] = json.load(open(_token_file))


def get_token(bot_name: str) -> str:
    return _tokens[bot_name]
