from rest_framework import serializers
from conversations.models import Conversation


class ConversationSerializer(serializers.ModelSerializer):
  class Meta:
    model = Conversation
    fields = (
      'conversation_id',
      'conversation_link',
      'transcript',
      'speaker_type',
      'dialog_id',
      'duration',
    )


class UserConversationSerializer(serializers.ModelSerializer):
  short_transcript = serializers.SerializerMethodField()

  class Meta:
    model = Conversation
    fields = (
      'conversation_id',
      'conversation_link',
      'short_transcript',
      'created_date',
      'modified_date',
      'duration'
    )

    def get_short_transcript(self, obj):
      max_length = 100
      transcript = obj.transcript
      if len(transcript) > max_length:
          return transcript[:max_length] + '...'
      return transcript