from pydub import AudioSegment
import whisper

model = whisper.load_model("base")

def convert_webm_to_wav(webm_path, wav_path):
    audio = AudioSegment.from_file(webm_path, format="webm")
    audio.export(wav_path, format="wav")

def transcribe_audio_file(file_path: str) -> str:
    result = model.transcribe(file_path)
    return result["text"]
