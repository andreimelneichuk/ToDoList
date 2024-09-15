from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User
from .models import Task, Category

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'due_date', 'category', 'is_completed', 'user')
    list_filter = ('is_completed', 'due_date', 'category')
    search_fields = ('title',)

class UserAdmin(DefaultUserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2')}
        ),
    )
    ordering = ('username',)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Task, TaskAdmin)
admin.site.register(Category)