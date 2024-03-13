import torch
import librosa
import requests
import numpy as np

# Save the entire conversation as an MP3 file
import soundfile as sf
from pydub import AudioSegment
from transformers import WhisperProcessor, WhisperForConditionalGeneration


checkpoint = "openai/whisper-base"


class Whisper():
    def __init__(self, model='Bert', version='1.0.0', LS=None, BIES=False):
        self.LS = LS
        self.model = WhisperForConditionalGeneration.from_pretrained(
            checkpoint)
        self.processor = WhisperProcessor.from_pretrained(checkpoint)

        # self.ner_model = BIOBERT('BioBERT', '1.0.0')

    def process_audio(self, sampling_rate, waveform):
        # convert from int16 to floating point
        waveform = waveform / 32678.0

        # convert to mono if stereo ## Librosa is for manipulation 
        if len(waveform.shape) > 1:
            waveform = librosa.to_mono(waveform.T)

        # resample to 16 kHz if necessary
        # if sampling_rate != 16000:
        #     waveform = librosa.resample(
        #         waveform, orig_sr=sampling_rate, target_sr=16000)

        # limit to 30 seconds
        waveform = waveform[:sampling_rate*30]

        # make PyTorch tensor
        waveform = torch.tensor(waveform)
        return waveform

    def load_audio_from_url(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            # Get the audio content as bytes
            audio_bytes = response.content

            # # Convert the audio bytes to an audio waveform array
            # audio, sample_rate = librosa.load(io.BytesIO(audio_bytes), sr=None)

            # print("sampling rate:", sample_rate)
            # Save the downloaded MP3 file
            with open("audio.mp3", "wb") as file:
                file.write(response.content)

            # Load the MP3 file using librosa
            audio_path = "audio.mp3"

            audio = AudioSegment.from_mp3(audio_path)

            sampling_rate = audio.frame_rate

            print("sampling rate:", sampling_rate)

            return audio, sampling_rate, audio_bytes

    def load_audio_from_bytes(self, audio_bytes):
      
        with open("audio.mp3", "wb") as file:
            file.write(audio_bytes)

        # Load the MP3 file using librosa
        audio_path = "audio.mp3"

        audio = AudioSegment.from_mp3(audio_path)

        sampling_rate = audio.frame_rate

        print("sampling rate:", sampling_rate)

        return audio, sampling_rate, audio_bytes

    def get_chunks(self, audio):

        # def apply_stride(output_path, stride_duration):
        # Load the MP3 audio file
        # audio = AudioSegment.from_mp3(output_path)

        # sampling_rate = audio.frame_rate

        # Set parameters for chunking
        chunk_duration = 30 * 1000  # 30 seconds in milliseconds
        stride_duration = 10 * 1000  # 10 seconds in milliseconds

        # Initialize variables
        start_time = 0

        # Initialize a list to store the audio chunks
        audio_chunks = []

        # Loop to split the audio into 30-second chunks with a stride of 10 seconds
        while start_time + chunk_duration <= len(audio):
            # Calculate the end time for the current chunk
            end_time = start_time + chunk_duration

            # Extract the audio segment for the current chunk
            audio_chunk = audio[start_time:end_time]

            # Add the audio chunk to the list
            audio_chunks.append(audio_chunk)

            # Update the start time for the next chunk
            # start_time += stride_duration
            start_time = end_time


        ## if the last chunk is less than 30 seconds, add it to the list
        if start_time < len(audio):
            audio_chunk = audio[start_time:len(audio)]
            audio_chunks.append(audio_chunk)

        return audio_chunks
    

    def extract(self, urls, language='english', mic_audio=None, files=None, path=False):
        extracted_data = []
        for id, url in enumerate(urls):
            if path:
                audio = AudioSegment.from_mp3(url)
                sampling_rate = audio.frame_rate
                print("sampling rate:", sampling_rate)
            elif files:
                audio, sampling_rate, audio_bytes = self.load_audio_from_bytes(url)
            else:
                audio, sampling_rate, audio_bytes = self.load_audio_from_url(url)

            audio_chunks = self.get_chunks(audio)

            print(len(audio_chunks))

            transcriptions = []

            for chunk_id, audio_chunk in enumerate(audio_chunks):
                forced_decoder_ids = self.processor.get_decoder_prompt_ids(
                    language=language, task="transcribe")

                waveform = self.process_audio(
                    sampling_rate, np.array(audio_chunk.get_array_of_samples()))
                inputs = self.processor(
                    audio=waveform, sampling_rate=16000, return_tensors="pt")
                predicted_ids = self.model.generate(
                    **inputs, max_length=400, forced_decoder_ids=forced_decoder_ids)
                transcription = self.processor.batch_decode(
                    predicted_ids, skip_special_tokens=True)
                
                print("transcription:", transcription)

                transcriptions.append(transcription)


                # print("chunk_id", chunk_id)
                # print("transcription","".join(transcription[0]))


                #set_task_status(task_id, 'transcribing', task_name='transcribing', percentage=0, output= { 'id' : id , 'chunk_id' : [chunk_id],  'audio' : base64.b64encode(audio_bytes).decode() , **self.ner_model.get_ner_relations(transcription[0])} )
                

            extracted_data.append(
                {'text': " ".join(chunk[0] for chunk in transcriptions), 'labels': []})
            
            #extracted_data.append({'audio' : base64.b64encode(audio_bytes).decode(), **self.ner_model.get_ner_relations( " ".join(chunk[0] for chunk in transcriptions))})

            # extracted_data.append({**self.ner_model.get_ner_relations( " ".join(chunk[0] for chunk in transcriptions), extract = True)})

        #set_task_status(task_id, 'completed', task_name='transcribing', percentage=0, output= [{'audio' : base64.b64encode(audio_bytes).decode() , **self.ner_model.get_ner_relations("".join(transcription[0]))} ])

        return extracted_data
