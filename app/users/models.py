from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, Permission

from authorization.models import Role

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email: str, role: Role | str, password: str | None = None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        
        if not role:
            raise ValueError("The Role field must be set")
        
        if isinstance(role, str):
            try:
                role = Role.objects.get(name=role)
            except Role.DoesNotExist:
                raise ValueError(f"Role '{role}' does not exist")
        
        email = self.normalize_email(email)
        user: "User" = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="users")
    #store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    first_login = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: UserManager = UserManager()

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_all_permissions(self, obj=None):
        if not self.is_active:
            return set()

        return {
            f"{permission.content_type.app_label}.{permission.codename}"
            for permission in self.role.permissions.select_related(
                "content_type"
            ).all()
        }

    def has_perm(self, perm, obj=None):
        if not self.is_active:
            return False

        return perm in self.get_all_permissions(obj)

    def __str__(self):
        return self.full_name