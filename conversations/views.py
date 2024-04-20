import asyncio
import json
import random

from datetime import datetime
from decimal import Decimal

from rest_framework import generics, filters, status
from rest_framework.response import Response
from rest_framework import status

from .models import Conversation
from .models import Dialog
from .serializers import ConversationSerializer
from .utils import LargeResultsSetPagination, get_aws_manager, get_formatted_audio, generate_audio_transcription, get_classified_speakers

from websocket.web_socket_helper import send_websocket_message

from users.models import User

class ConversationListCreateView(generics.ListCreateAPIView):
  queryset = Conversation.objects.all()
  serializer_class = ConversationSerializer
  pagination_class = LargeResultsSetPagination
  counter = 0
  filter_backends = [filters.SearchFilter, filters.OrderingFilter]
  search_fields = [
    'conversation_id',
    'duration'
  ]
  ordering_fields = ['conversation_id', 'created_date', 'duration', 'modified_date']      

  def create(self, request, *args, **kwargs):
    try:
        self.process_request(request)
        return Response({"Message": "Transcript and User records created successfully"}, status=status.HTTP_201_CREATED)
    except Exception as error:
        return Response({"Message": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

  def process_request(self, request):
    user_data = request.data
    audio_file = user_data.pop('audio', None)[0]
    is_first = user_data.pop('first', False)[0]
    is_last = user_data.pop('last', False)[0]
    user_data = user_data.dict()
    duration = Decimal(user_data.pop('duration'))
    user_data['is_update'] = bool(user_data['is_update'])

    if not audio_file or not user_data:
        raise Exception("No audio file or user data provided")
    
    user, created = User.objects.get_or_create(user_id=user_data.get('user_id'), defaults=user_data)
    created_date = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    audio_data = audio_file.read()
    
    get_formatted_audio(audio_data, is_first, duration)
    
    aws_manager = get_aws_manager('s3')
    filename = f"audio.{created_date}.{user.user_id}.wav"

    if is_first == 'True':
      dialog_id = Dialog.objects.create(user_id=user, state="IN_PROGRESS" if is_last == 'False' else "CLOSED")
    else:
      dialog_id = Dialog.objects.get(pk=Dialog.objects.latest('id').id)

      if is_last == "True":
        dialog_id.state = "CLOSED"
        dialog_id.save()

    s3_url = aws_manager.upload_audio(filename, open('audio.wav', 'rb'))
    presigned_url = aws_manager.generate_presigned_url(filename)
    transcript = generate_audio_transcription(presigned_url, dialog_id.id, s3_url, duration)
    
    if transcript is None or transcript == '':
      raise Exception("No context found in audio")
    
    classified_data = json.loads(get_classified_speakers(transcript).replace('salesman', 'sales_person'))

    if not isinstance(classified_data, list) or not all(isinstance(item, dict) for item in classified_data):
      raise Exception("AI Classified Response is not a valid JSON array of objects")
    
    print("\n\n\nAI Classified Response is a valid JSON array of objects.\n\n\n", classified_data, '\n\n\n')
    
    conversation_saved = self.save_conversation(dialog_id, s3_url, duration, classified_data, user)

    if conversation_saved is True:
      self.send_ws_message(is_first, is_last, user_data, dialog_id, user, classified_data)

  def save_conversation(self, dialog_id, s3_url, duration, classified_data, user):
    sorted_transcript_data = sorted(classified_data, key=lambda item: item.get('transcript_order', 0))

    duration = round(duration/len(sorted_transcript_data), 2)

    for transcript_item in sorted_transcript_data:
      serializer = ConversationSerializer(data={
        'speaker_type': transcript_item['speaker_type'],
        'transcript': transcript_item['transcript'],
        'dialog_id': dialog_id.id,
        'user_id': user.user_id,
        'conversation_link': s3_url,
        'duration': duration,
      })

      if serializer.is_valid():
        serializer.save()
      else:
        raise Exception(serializer.errors)
    
    return True

  def send_ws_message(self, is_first, is_last, user_data, dialog_id, user, classified_data):
    if is_first == "True":
      colors = ['#00BE08', '#FFB526',  '#4256D0', '#DC2626', '#C400E4'] 
      user_data['state'] = random.choice(colors)
      
      socket_active_user_data = {
        "event_type": "new_active_user",
        "user": user_data,
        "dialog_id": dialog_id.id,
        "room_name": user.dealer_name,
      }

      asyncio.run(send_websocket_message(socket_active_user_data))

    socket_active_conversation_data = {
      "event_type": "new_conversation_chunk",
      "user_id": str(user.user_id),
      "dialog_id": dialog_id.id,
      "data": classified_data,
      "room_name": user.dealer_name,
    }


    if is_last == "True":
      socket_active_conversation_data["is_last"] = "True"

    asyncio.run(send_websocket_message(socket_active_conversation_data))

    
class ConversationRetrieveView(generics.RetrieveAPIView):
  serializer_class = ConversationSerializer
  http_method_names = ['get']
  lookup_field = 'conversation_id'
  pagination_class = LargeResultsSetPagination

  def get_queryset(self):
    conversation_id = self.kwargs['conversation_id']
    try:
        conversation = Conversation.objects.get(pk=conversation_id)
        return Conversation.objects.filter(conversation_id=conversation.conversation_id)
    except Conversation.DoesNotExist:
        return Conversation.objects.none()

  def retrieve(self, request, *args, **kwargs):
    queryset = self.get_queryset()
    if not queryset.exists():
        return Response({'message': 'Invalid conversation id'}, status= status.HTTP_400_BAD_REQUEST)
    
    serializer = ConversationSerializer(queryset, many=True)
    return Response(serializer.data[0])

class DialogConversationsAPIView(generics.ListAPIView):
  serializer_class = ConversationSerializer
  http_method_names = ['get']
  lookup_field = 'dialog_id'
  pagination_class = LargeResultsSetPagination

  def get_queryset(self):
    try:
      dialog_id = self.kwargs['dialog_id']
      return Conversation.objects.filter(dialog_id=dialog_id).order_by('created_date')
    except Conversation.DoesNotExist:
      return Conversation.objects.none()

  def retrieve(self, request, *args, **kwargs):
    queryset = self.get_queryset()
    if not queryset.exists():
      return Response({'message': 'Invalid dialog id'}, status= status.HTTP_400_BAD_REQUEST)
    
    serializer = ConversationSerializer(queryset, many=True)
    return Response(serializer.data)


