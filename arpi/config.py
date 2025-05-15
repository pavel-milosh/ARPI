import json
from typing import Any

_: dict[str, Any] = json.load(open("config.json"))
