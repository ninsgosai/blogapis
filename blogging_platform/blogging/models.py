
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from utils.custom_manager import UserManager
from django.core import signing
from django.contrib.auth.models import Permission, Group, PermissionsMixin
from django_lifecycle import LifecycleModelMixin, BEFORE_UPDATE, BEFORE_CREATE, hook
from django.utils.text import slugify
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _


class Role(models.Model, LifecycleModelMixin):
    role_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=500)
    is_system_defined = models.BooleanField(default=False)
    permissions = models.ManyToManyField(
        Permission, verbose_name=_('Role Permissions'), blank=True, help_text=_('Specific permissions for this role.'),
        related_name="role_set", related_query_name="roles")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    @hook(BEFORE_UPDATE, when='role_name', has_changed=True)
    @hook(BEFORE_CREATE)
    def do_after_create_jobs(self):
        self.slug = slugify(self.role_name)

    def get_sign_pk(self):
        return signing.dumps(self.pk)

    @cached_property
    def is_deletable(self):
        return False if self.users.count() else True

    def __str__(self) -> str:
        return f'{self.role_name}'


class Users(AbstractBaseUser, PermissionsMixin):
    """
        An abstract base class implementing a fully featured User model with
        admin-compliant permissions.

        Email and password are required. Other fields are optional.
    """

    role = models.ForeignKey(Role, related_name="blog_users", on_delete=models.SET_NULL, verbose_name=_("Role"),
                             blank=True, null=True)
    name = models.CharField(blank=True, null=True, max_length=256)
    username = models.CharField(max_length=256, blank=True, null=True)
    email = models.EmailField(max_length=50, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    is_staff = models.BooleanField(
        "staff status",
        default=False,
        help_text="Designates whether the user can log into this admin site.",
    )

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"

    def get_sign_pk(self):
        return signing.dumps(self.pk)

    class Meta:
        db_table = "users"
        verbose_name = 'users'
        verbose_name_plural = 'Users'


class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    publication_date = models.DateTimeField()
    author = models.ForeignKey(Users, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-publication_date']


class Comment(models.Model):
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)
    author = models.ForeignKey(Users, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

