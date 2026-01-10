from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User  # your custom user model

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'full_name', 'role', 'employee_id', 'department', 'is_active_employee')
    list_filter = ('role', 'is_active_employee', 'department', 'date_joined_company')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'employee_id')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Employment info', {
            'fields': ('role', 'employee_id', 'department', 'position', 'phone_number', 'date_joined_company', 'is_active_employee')
        }),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    readonly_fields = ('employee_id', 'date_joined', 'last_login')

    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Full Name'
