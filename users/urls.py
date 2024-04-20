from django.urls import path

from users.views import (
  UserListAPIView,
  ActiveUserListAPIView,
  # UserDetailAPIView,
  UserDialogListAPIView,
  ActiveConversationsAPIView
)

app_name = "users"

urlpatterns = [
  path('', UserListAPIView.as_view(), name='list_user'),
  path('/active', ActiveUserListAPIView.as_view(), name='active_users'),
  path('/<int:user_id>/transcripts', UserDialogListAPIView.as_view(), name='user-conversation-list'),
  path('/<int:user_id>/transcripts/active', ActiveConversationsAPIView.as_view(), name="user-active-conversation-list")
]
