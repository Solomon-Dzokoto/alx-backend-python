from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Conversation, Message, User
from .serializers import ConversationSerializer, MessageSerializer, UserSerializer
from .permissions import IsAuthenticatedAndParticipant
from .filters import MessageFilter, ConversationFilter
from .pagination import MessagesPagination


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all().prefetch_related('participants', 'messages')
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticatedAndParticipant]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ConversationFilter
    ordering_fields = ['created_at']
    pagination_class = MessagesPagination

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
    permission_classes = [IsAuthenticatedAndParticipant]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = MessageFilter
    ordering_fields = ['sent_at']
    pagination_class = MessagesPagination

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
