from enum import Enum

"""  Roles
Super Admin : Root User
Admin :  Create from super admin
Guest :  Normal user

"""


class RoleEnum(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    GUEST = "GUEST"
