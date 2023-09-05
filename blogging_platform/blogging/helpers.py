from blogging import custom_permissions
from django.contrib.auth.models import Permission


def create_system_roles():
    from blogging.models import Role

    all_permissions = Permission.objects.select_related('content_type').all()

    end_user, created = Role.objects.get_or_create(role_name="Administrators", is_system_defined=True)
    end_user_permissions = all_permissions.filter(codename__in=custom_permissions.CONTENT_TYPE_INCLUDE)
    end_user.permissions.set(end_user_permissions)

    app_user, created = Role.objects.get_or_create(role_name="Regular User", is_system_defined=True)
    app_user_permissions = all_permissions.filter(codename__in=custom_permissions.APP_USER_PERMISSIONS)
    app_user.permissions.set(app_user_permissions)
