import django_filters
from django.db.models import Q
from .models import Message, Conversation, User


class MessageFilter(django_filters.FilterSet):
    start = django_filters.IsoDateTimeFilter(field_name='sent_at', lookup_expr='gte')
    end = django_filters.IsoDateTimeFilter(field_name='sent_at', lookup_expr='lte')
    sender = django_filters.UUIDFilter(field_name='sender__id')
    conversation = django_filters.UUIDFilter(field_name='conversation__id')

    class Meta:
        model = Message
        fields = ['start', 'end', 'sender', 'conversation']


class ConversationFilter(django_filters.FilterSet):
    participant = django_filters.UUIDFilter(method='filter_by_participant')

    class Meta:
        model = Conversation
        fields = ['participant']

    def filter_by_participant(self, queryset, name, value):
        return queryset.filter(participants__id=value)
