from typing import Any

# Generic schema
from app.schemas import GenericSchema

GET_USER_4XX_RESPONSES: Any = {
    401: {
        "model": GenericSchema.DetailResponse,
        "description": "Could not validate credentials",
    },
    403: {
        "model": GenericSchema.DetailResponse,
        "description": "Not enough permissions",
    },
}
