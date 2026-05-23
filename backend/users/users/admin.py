from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


admin.site.site_header = "HireSenseAI Administration"
admin.site.site_title = "HireSenseAI Admin"
admin.site.index_title = "Operations Console"


class HireSenseUserAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "is_active", "date_joined")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups", "date_joined")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-date_joined",)


admin.site.unregister(User)
admin.site.register(User, HireSenseUserAdmin)
