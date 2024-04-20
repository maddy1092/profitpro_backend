
import openai
import os
import subprocess
import requests
import wave

from pydub import AudioSegment

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from aws_operations.s3_operations import AWSClientManager


openai.api_key = os.environ.get("OPENAI_API_KEY")
class LargeResultsSetPagination(PageNumberPagination):
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


def get_aws_manager(service_name):
  aws_manager = AWSClientManager(
    service_name=service_name,
    region_name=os.environ.get("AWS_S3_REGION"),
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY")
  )
  return aws_manager

def convert_mp3_to_wav():
  command = ["ffmpeg", "-i", "combined_audio.mp3", "-y", "combined_audio.wav"]

  try:
    subprocess.run(command, check=True)
    print(f"Conversion from mp3 to wav completed successfully.")
  except subprocess.CalledProcessError as e:
    print(f"Error while converting: {e}")
  except FileNotFoundError as e:
    print(f"ffmpeg not found. Make sure ffmpeg is installed and in your PATH.")\

def get_formatted_audio(audio_data, is_first, duration):
  if audio_data:
    if is_first=='True':
      with open("combined_audio.wav", "wb") as file:
        file.write(audio_data)

      chunk_one = AudioSegment.from_file("combined_audio.wav")
      print('first chunk length', len(chunk_one)/1000)
      wav_output_path = "audio.wav"
      chunk_one.export(wav_output_path, format="wav")
    else:
      combine_wav_files("combined_audio.wav", audio_data, "combined_audio.wav")
        
      original_audio = AudioSegment.from_file("combined_audio.wav")
      
      wav_output_path = "audio.wav"
      original_audio.export(wav_output_path, format="wav")    

def combine_wav_files(original_wav_path, chunk_data, output_wav_path):
    original_wav = wave.open(original_wav_path, 'rb')
    
    original_params = original_wav.getparams()

    output_wav = wave.open(output_wav_path, 'wb')

    output_wav.setparams(original_params)
    # output_wav.writeframes(original_wav.readframes(original_params.nframes))
    output_wav.writeframes(chunk_data)

    original_wav.close()
    output_wav.close()

def generate_audio_transcription(presigned_url, dialog_id ,s3_url, duration):
  url = os.environ.get("OPENAI_URL")
  payload = {
    'model': os.environ.get("OPENAI_MODEL"),
    'prompt': os.environ.get("OPENAI_PROMPT"),
    'language': os.environ.get("OPENAI_LANGUAGE"),
    'temperature': os.environ.get("OPENAI_AUDIO_TEMPERATURE"),
  }

  files = [
    ('file',('audio.wav',  open('audio.wav', 'rb'),'audio/wav'))
  ]
  headers = { 'Authorization': "Bearer " + os.environ.get("OPENAI_API_KEY") }
 
  transcript = requests.request("POST", url, headers=headers, data=payload, files=files).json()

  if transcript and transcript['text']:
    data = transcript['text']
    print('Generated Transcript: ',data)
  else:
    data = None

  return data

def get_classified_speakers(transcription):
  completion = openai.ChatCompletion.create(
    model = "gpt-3.5-turbo-16k", 
    messages = [{
      "role": "user",
      "content" : f'''Following is transcription text of conversation between a salesman and a customer \n\n
        Conversation:  ```{transcription}``` \n\n
        I want you to classify above conversation inside qoutes in the following pattern: - \n
        ```{{
            "speaker_type": "customer",
            "transcript": "customer transcript here...",
            "transcript_order": 2
            }}```\n
        and return an array of such objects. It should be only array in response, no text else should be in your response.
        '''
    }]
  )

  return completion["choices"][0]["message"]["content"]