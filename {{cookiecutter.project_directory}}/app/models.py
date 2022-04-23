from tortoise import fields, models
from app.constants import RoleEnum

################################################################################
#                          User
################################################################################


class User(models.Model):
    id = fields.IntField(pk=True, index=True)
    name = fields.CharField(max_length=50)
    email = fields.CharField(max_length=50, unique=True, index=True)
    password_hash = fields.CharField(max_length=128)
    is_active = fields.BooleanField(default=False)
    is_admin = fields.BooleanField(default=False)

    roles: fields.ManyToManyRelation["Role"] = fields.ManyToManyField(
        "models.Role",
        related_name="users",
        on_delete=fields.CASCADE,
    )

    class Meta:
        table = "users"

    def __str__(self):
        return f"User(id={self.id}, name={self.name})"


################################################################################
#                          Role
################################################################################
class Role(models.Model):
    id = fields.UUIDField(pk=True, index=True)
    name = fields.CharEnumField(RoleEnum, index=True)

    users: fields.ManyToManyRelation[User]

    class Meta:
        table = "roles"

    def __str__(self):
        return f"Role(id={self.id}, name={self.name})"
