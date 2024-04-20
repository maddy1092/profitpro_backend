from django.contrib import admin

from .models import Conversation
from .models import Dialog

class ConversationAdmin(admin.ModelAdmin):
  list_display = ['conversation_id', 'created_date', 'modified_date', 'duration', 'conversation_link', 'dialog_id', 'transcript']
  list_filter = ['conversation_id', 'created_date']
  search_fields = ['conversation_id', 'dialog_id']
  fieldsets = (
    (None, {
        'fields': ('conversation_link', 'speaker_type', 'dialog_id', 'duration')
    }),
  )


class DialogAdmin(admin.ModelAdmin):
  list_display = ['user_id']

admin.site.register(Conversation, ConversationAdmin)
admin.site.register(Dialog, DialogAdmin)