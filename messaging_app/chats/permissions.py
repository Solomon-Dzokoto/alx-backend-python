from rest_framework import permissions
from .models import Conversation


class IsAuthenticatedAndParticipant(permissions.BasePermission):
    """Allow access only to authenticated users who are participants of a conversation.

    For viewsets that act on Conversation instances, checks that the requesting
    user is in the conversation.participants. For message-level actions, it
    also ensures the user is a participant of the related conversation.
    """

    def has_permission(self, request, view):
        # Require authentication globally
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # obj may be Conversation or Message
        if isinstance(obj, Conversation):
            return request.user in obj.participants.all()

        # Otherwise assume message-like object with conversation attribute
        conv = getattr(obj, 'conversation', None)
        if conv is not None:
            return request.user in conv.participants.all()

        return False
