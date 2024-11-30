from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from users.models import User, TgUserToken


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ('phone', 'full_name', 'tg_id')
    readonly_fields = ('phone',)
    search_fields = ('phone', 'full_name')
    fieldsets = (
        (_("Personal info"),
         {'fields': (
             'full_name',
             'phone',
             'role',
             'tg_id',
             'tg_username',
         )}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",

                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )


@admin.register(TgUserToken)
class TgUserTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at')
    # def has_module_permission(self, request):
    #     return False
