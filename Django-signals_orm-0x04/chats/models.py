import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """Custom user model extending AbstractUser.

    Uses UUID primary key and adds phone_number and role.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # AbstractUser already includes first_name, last_name, email, password
    phone_number = models.CharField(max_length=32, null=True, blank=True)

    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='guest')

    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        indexes = [models.Index(fields=['email'])]
        verbose_name = 'user'
        verbose_name_plural = 'users'


class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField('User', related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Conversation {self.id}'


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey('User', on_delete=models.CASCADE, related_name='sent_messages')
    # Optional receiver for direct one-to-one messages. If not set, message is part of a conversation
    receiver = models.ForeignKey('User', on_delete=models.CASCADE, null=True, blank=True, related_name='received_messages')
    conversation = models.ForeignKey('Conversation', on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    message_body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    # mark if the message was edited after creation
    edited = models.BooleanField(default=False)
    # mark whether the recipient has read the message
    read = models.BooleanField(default=False)
    # parent message for threaded replies
    parent_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    objects = models.Manager()

    class UnreadMessagesManager(models.Manager):
        def for_user(self, user):
            return self.get_queryset().filter(receiver=user, read=False)

    unread = UnreadMessagesManager()

    def __str__(self):
        return f'Message {self.id} by {self.sender}'


class MessageHistory(models.Model):
    """Stores previous versions of a Message when it's edited."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey('Message', on_delete=models.CASCADE, related_name='history')
    old_content = models.TextField()
    edited_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'History for {self.message_id} at {self.edited_at}'


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey('Message', on_delete=models.CASCADE, related_name='notifications')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Notification for {self.user} about message {self.message_id}'
