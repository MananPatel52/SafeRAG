import json
import logging
from typing import Any


logger = logging.getLogger("saferag")


def log_event(
    event: str,
    **fields: Any,
) -> None:
    """
    Emit a structured SafeRAG observability event.
    """

    payload = {
        "event": event,
        **fields,
    }

    logger.info(
        json.dumps(
            payload,
            default=str,
        )
    )