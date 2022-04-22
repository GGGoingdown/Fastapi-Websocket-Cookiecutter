#################################################################################
#                           Save Exception
#################################################################################
class SaveError(Exception):
    entity_name: str

    def __init__(self, entity_id):
        class_name = self.__class__.__name__
        super().__init__(
            f"[{class_name}]::Save {self.entity_name} error, Get: {entity_id}"
        )


class CacheUserError(SaveError):
    entity_name: str = "user"


class CacheTokenError(SaveError):
    entity_name: str = "auth"


class SaveDBUserError(SaveError):
    entity_name: str = "user"


#################################################################################
#                           Get Exception
#################################################################################
class NotFoundError(Exception):
    entity_name: str

    def __init__(self):
        class_name = self.__class__.__name__
        super().__init__(f"[{class_name}]::Get {self.entity_name} error")


class RoleNotFoundError(NotFoundError):
    entity_name: str = "role"


class ActiveTokenNotFoundError(NotFoundError):
    entity_name: str = "active-token"


#################################################################################
#                           Update Exception
#################################################################################
class UpdateError(Exception):
    entity_name: str

    def __init__(self, entity_id):
        class_name = self.__class__.__name__
        super().__init__(
            f"[{class_name}]::Update {self.entity_name} error. ID: {entity_id}"
        )


class UserUpdateError(UpdateError):
    entity_name: str = "user"


if __name__ == "__main__":
    print(CacheUserError(None))
