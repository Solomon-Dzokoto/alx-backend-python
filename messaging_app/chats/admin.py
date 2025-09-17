from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, Conversation, Message


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User
    fieldsets = DjangoUserAdmin.fieldsets + (
        (None, {'fields': ('phone_number', 'role', 'created_at')}),
    )


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    filter_horizontal = ('participants',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'conversation', 'sent_at')
