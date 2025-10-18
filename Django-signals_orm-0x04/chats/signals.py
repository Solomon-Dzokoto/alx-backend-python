from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from .models import Message, Notification, MessageHistory
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=Message)
def create_notification_on_message(sender, instance, created, **kwargs):
    """Create a Notification for the receiver when a new Message is created."""
    if not created:
        return
    receiver = instance.receiver
    if receiver:
        Notification.objects.create(user=receiver, message=instance)


@receiver(pre_save, sender=Message)
def log_message_history_on_edit(sender, instance, **kwargs):
    """Before a Message is updated, store its old content into MessageHistory."""
    if not instance.pk:
        # new message, nothing to log
        return
    try:
        old = Message.objects.get(pk=instance.pk)
    except Message.DoesNotExist:
        return

    # If content changed and it's not the initial save
    if old.message_body != instance.message_body:
        # create a history record with the old content
        MessageHistory.objects.create(message=old, old_content=old.message_body)
        # mark edited flag
        instance.edited = True


@receiver(post_delete, sender=User)
def cleanup_user_related(sender, instance, **kwargs):
    """Clean up messages, notifications and histories related to a deleted user.

    Use CASCADE on FK so most will delete automatically; ensure any orphaned
    MessageHistory or Notification entries are removed if necessary.
    """
    # Messages where user was sender or receiver are cascade-deleted by FK
    # But to be explicit, delete related notifications and histories
    Notification.objects.filter(user=instance).delete()
    MessageHistory.objects.filter(message__sender=instance).delete()
    MessageHistory.objects.filter(message__receiver=instance).delete()