from functools import lru_cache
from pydantic import BaseModel, validator
from typing import Union
from enum import IntEnum


class SaveErrorIntEnum(IntEnum):
    SAVE_CACHE_ERROR = 1101


class GetErrorIntEnum(IntEnum):
    NOT_FOUND_ERROR = 2101


class UpdateErrorIntEnum(IntEnum):
    UPDATE_ERROR = 3101


class DeleteErrorIntEnum(IntEnum):
    ...


class BaseErrorCode(BaseModel):
    code: Union[
        SaveErrorIntEnum,
        GetErrorIntEnum,
        UpdateErrorIntEnum,
        DeleteErrorIntEnum,
    ]

    @validator("code")
    def to_value(cls, v):
        return v.value

    description: str


############################################################################################
#                               Error codes
############################################################################################
# Error code: 1101 - Save chache error
_save_cache_error = BaseErrorCode(
    code=SaveErrorIntEnum.SAVE_CACHE_ERROR,
    description="Save data in cache error",
)

_not_found_error = BaseErrorCode(
    code=GetErrorIntEnum.NOT_FOUND_ERROR, description="Get data not found error"
)

_update_error = BaseErrorCode(
    code=UpdateErrorIntEnum.UPDATE_ERROR, description="Update data error"
)

#############################################################################################
class ErrorCodes(BaseModel):
    SAVE_CACHE_ERROR: BaseErrorCode
    NOT_FOUND_ERROR: BaseErrorCode
    UPDATE_ERROR: BaseErrorCode


@lru_cache(maxsize=20)
def get_error_codes() -> ErrorCodes:
    return ErrorCodes(
        SAVE_CACHE_ERROR=_save_cache_error,
        NOT_FOUND_ERROR=_not_found_error,
        UPDATE_ERROR=_update_error,
    )


ERROR_CODES = get_error_codes()


if __name__ == "__main__":
    print(ERROR_CODES.SAVE_CACHE_ERROR.code)
