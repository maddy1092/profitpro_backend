from django.urls import path

from conversations.views import (
  ConversationListCreateView,
  DialogConversationsAPIView
)

app_name = "conversations"
urlpatterns = [
  path('', ConversationListCreateView.as_view(), name='list_create_conversion'),
  path('/<int:dialog_id>', DialogConversationsAPIView.as_view(), name='dialog_conversations'),
]
