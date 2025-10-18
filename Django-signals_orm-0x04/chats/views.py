from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from .models import Conversation, Message, User
from .serializers import ConversationSerializer, MessageSerializer, UserSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all().prefetch_related('participants', 'messages')
    serializer_class = ConversationSerializer

    def create(self, request, *args, **kwargs):
        # Expect participants as list of user ids in request.data['participants']
        participant_ids = request.data.get('participants', [])
        if not isinstance(participant_ids, list) or len(participant_ids) < 1:
            return Response({'detail': 'participants must be a list of user ids'}, status=status.HTTP_400_BAD_REQUEST)

        conv = Conversation.objects.create()
        users = User.objects.filter(id__in=participant_ids)
        conv.participants.set(users)
        conv.save()
        serializer = self.get_serializer(conv)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().select_related('sender', 'conversation')
    serializer_class = MessageSerializer

    def create(self, request, *args, **kwargs):
        # Expect 'sender' to be user id and 'conversation' to be conversation id
        sender_id = request.data.get('sender')
        conversation_id = request.data.get('conversation')
        body = request.data.get('message_body')

        if not sender_id or not conversation_id or not body:
            return Response({'detail': 'sender, conversation and message_body are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            sender = User.objects.get(id=sender_id)
            conv = Conversation.objects.get(id=conversation_id)
        except User.DoesNotExist:
            return Response({'detail': 'sender not found'}, status=status.HTTP_404_NOT_FOUND)
        except Conversation.DoesNotExist:
            return Response({'detail': 'conversation not found'}, status=status.HTTP_404_NOT_FOUND)

        msg = Message.objects.create(sender=sender, conversation=conv, message_body=body)
        serializer = self.get_serializer(msg)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def delete_user(request):
    """Delete the requesting user account. Expects 'user_id' in POST data.

    This triggers the User.post_delete signal to clean up related data.
    """
    user_id = request.data.get('user_id')
    if not user_id:
        return Response({'detail': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'detail': 'user not found'}, status=status.HTTP_404_NOT_FOUND)

    # Delete user (will trigger post_delete signal)
    user.delete()
    return Response({'detail': 'user deleted'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@cache_page(60)  # cache for 60 seconds
def cached_conversation_messages(request, conversation_id):
    """Return messages for a conversation (cached for 60s)."""
    try:
        conv = Conversation.objects.prefetch_related('messages__sender').get(id=conversation_id)
    except Conversation.DoesNotExist:
        return Response({'detail': 'conversation not found'}, status=status.HTTP_404_NOT_FOUND)
    msgs = conv.messages.select_related('sender').only('id', 'sender_id', 'message_body', 'sent_at', 'parent_message')
    serializer = MessageSerializer(msgs, many=True)
    return Response(serializer.data)
