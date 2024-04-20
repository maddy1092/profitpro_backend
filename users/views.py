from django.db.models import Sum

from rest_framework.pagination import PageNumberPagination
from rest_framework import generics, filters
from rest_framework.response import Response

from conversations.models import Conversation, Dialog
from conversations.serializers import ConversationSerializer
from users.models import User as Users
from users.models import User
from users.serializers import UserSerializer


class CustomPagination(PageNumberPagination):
  page_size = 100
  page_size_query_param = 'page_size'
  max_page_size = 100

  def get_paginated_response(self, data):
    return Response({
      'count': self.page.paginator.count,
      'current': self.page.number,
      'next': self.get_next_link(),
      'previous': self.get_previous_link(),
      'results': data,
    })


class UserListAPIView(generics.ListAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'first_name',
        'last_name',
        'user_email',
        'user_display_name',
    ]
    ordering_fields = ['first_name', 'mobile_number']

    def list(self, request, *args, **kwargs):
        queryset = super().get_queryset()
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)

        response_data = []
        
        for user in serializer.data:
            dialogs = Dialog.objects.filter(user_id=user['user_id'], state="CLOSED")
            dialog_data = []
            
            for dialog in dialogs:
                conversation = Conversation.objects.filter(dialog_id=dialog.id).first()
                total_duration = Conversation.objects.filter(dialog_id=dialog.id).aggregate(total_duration=Sum('duration'))['total_duration']
            
                if total_duration is not None:
                    duration = round(total_duration, 2)
                else:
                    duration = conversation.duration
                
                if conversation:
                    data = {
                        "dialog_id": dialog.id,
                        "created_at": conversation.created_date,
                        "updated_at": conversation.modified_date,
                        "conversation_url": conversation.conversation_link,
                        "duration": duration,
                    }

                    dialog_data.append(data)

            total_conversation_count = len(dialog_data)
            user['transcripts'] = dialog_data
            user['total_transcript_count'] = total_conversation_count
            
            response_data.append(user)

        return self.get_paginated_response(response_data)

class UserDialogListAPIView(generics.ListAPIView):
    pagination_class = CustomPagination
    
    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Dialog.objects.filter(user_id=user_id, state="CLOSED")

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        response_data = []
        for dialog in page:
            conversation = Conversation.objects.filter(dialog_id=dialog.id).first()
            total_duration = Conversation.objects.filter(dialog_id=dialog.id).aggregate(total_duration=Sum('duration'))['total_duration']
            
            if total_duration is not None:
                duration = round(total_duration, 2)
            else:
                duration = conversation.duration

            if conversation:
                data = {
                    "dialog_id": dialog.id,
                    "created_at": conversation.created_date,
                    "updated_at": conversation.modified_date,
                    "conversation_url": conversation.conversation_link,
                    "duration": duration,
                }

                response_data.append(data)

        return self.get_paginated_response(response_data)


class ActiveUserListAPIView(generics.ListAPIView):
    serializer_class = UserSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        active_users = Dialog.objects.filter(state='IN_PROGRESS').values('user_id').distinct()
        return User.objects.filter(user_id__in=active_users)


class ActiveConversationsAPIView(generics.ListAPIView):
    serializer_class = ConversationSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        dialogs = Dialog.objects.filter(user_id=user_id, state="IN_PROGRESS")
        
        return Conversation.objects.filter(dialog_id__in=dialogs).order_by('created_date')

