from __future__ import annotations

import json
import logging
import time
from typing import Any


logger = logging.getLogger("troubleshooting-agent")
logging.basicConfig(level=logging.INFO, format="%(message)s")


class Telemetry:
    def event(self, name: str, attributes: dict[str, Any]) -> None:
        payload = {
            "event": name,
            "timestamp": time.time(),
            "attributes": attributes,
        }
        logger.info(json.dumps(payload, default=str))


telemetry = Telemetry()
