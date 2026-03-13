from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC

model_id = "dysata/Wav2Vec2-Ru-Child"
print(f"Downloading {model_id}...")
# This forces the download during build time
model = Wav2Vec2ForCTC.from_pretrained(model_id)
processor = Wav2Vec2Processor.from_pretrained(model_id)
print("Download complete!")

