from flask import Flask, request, jsonify
from transformers import AutoTokenizer, PegasusXForConditionalGeneration
from flask_cors import CORS
import re
import nltk
from nltk.corpus import stopwords
import requests

from pytube import YouTube
import os
import torch
import whisper

# Download NLTK stopwords
nltk.download('stopwords')

app = Flask(__name__)
CORS(app, resources={r'*': {'origins': '*'}})

device = 'cuda' if torch.cuda.is_available() else 'cpu'
model_name = "google/pegasus-x-large"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = PegasusXForConditionalGeneration.from_pretrained(model_name)

# Use NLTK stopwords
stopwords = set(stopwords.words('english'))

def remove_stopwords(text):
    text = re.sub(r'\b(?:' + '|'.join(stopwords) + r')\b', '', text)
    return re.sub(' +', ' ', text)

def split_text(text, max_chunk_length):
    # Split the text into chunks of maximum length
    chunks = []
    words = text.split()
    current_chunk = ""
    counter = 0
    for word in words:
        if counter + 1 < max_chunk_length:
            current_chunk += word + " "
            counter+=1
        else:
            chunks.append(current_chunk.strip())
            current_chunk = word + " "
            counter = 0
    chunks.append(current_chunk.strip())
    print("there are {} chunks".format(len(chunks)))
    return chunks

def generate_summary(text_chunks):
    summary = ""
    counter = 0
    for chunk in text_chunks:
        print("summarizing chunk ", counter)
        print("encoding")
        inputs = tokenizer(chunk, return_tensors="pt")
        print("generating")
        summary_ids = model.generate(inputs["input_ids"])
        print("decoding")
        chunk_summary = tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
        summary += chunk_summary + " "
        # print(summary)
        counter += 1
    return summary

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.get_json()
    url = data['url']
    yt = YouTube(url)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download(filename="audio.wav")
    print("loading model")
    try:
        model = whisper.load_model("tiny")
    except Exception as e:
        print(f"Error loading model: {e}")
    print("loaded model")
    
    transcript = model.transcribe("audio.wav")
    return jsonify({'transcript': transcript})
    

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    transcript = data['transcript']
    # print("Received transcript:", transcript)

    # Remove stopwords from the input text
    print(type(transcript), transcript["text"])
    transcript = remove_stopwords(transcript["text"])

    max_chunk_length = 100  # Adjust the chunk length as needed
    text_chunks = split_text(transcript, max_chunk_length)
    print("text chunks: ", text_chunks)
    # Generate summary for the text chunks
    summary = generate_summary(text_chunks)
    print(summary)
    return jsonify({'summary': summary})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
