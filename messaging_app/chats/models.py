import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


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
    conversation = models.ForeignKey('Conversation', on_delete=models.CASCADE, related_name='messages')
    message_body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message {self.id} by {self.sender}'
