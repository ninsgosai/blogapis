from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Users)
admin.site.register(Role)
admin.site.register(BlogPost)
admin.site.register(Comment)