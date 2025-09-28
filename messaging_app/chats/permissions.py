from rest_framework import permissions
from .models import Conversation


class IsParticipantOfConversation(permissions.BasePermission):
    """Custom permission that allows only authenticated users who are
    participants of a conversation to view, send, update or delete messages.

    This explicitly checks mutating methods (PUT, PATCH, DELETE) as requested.
    """

    MUTATING_METHODS = ("PUT", "PATCH", "DELETE")

    def has_permission(self, request, view):
        # Only authenticated users may proceed to object checks
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # obj can be a Conversation or a Message
        # For Conversation, user must be in participants
        if isinstance(obj, Conversation):
            return request.user in obj.participants.all()

        # Otherwise assume message-like object with a conversation attribute
        conv = getattr(obj, 'conversation', None)
        if conv is not None:
            # For any read or write action, ensure the user is a participant
            if request.method in self.MUTATING_METHODS:
                # user must be participant to mutate
                return request.user in conv.participants.all()
            # for safe methods also require participant
            return request.user in conv.participants.all()

        return False

