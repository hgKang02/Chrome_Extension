from flask import Flask, request, jsonify
from transformers import PegasusForConditionalGeneration, AutoTokenizer
from flask_cors import CORS
import re
import nltk
from nltk.corpus import stopwords
import requests

from pytube import YouTube
import os
import whisper

# Download NLTK stopwords
nltk.download('stopwords')

app = Flask(__name__)
CORS(app, resources={r'*': {'origins': '*'}})

model_name = "google/pegasus-x-large"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = PegasusForConditionalGeneration.from_pretrained(model_name)

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
    for word in words:
        if len(current_chunk) + len(word) < max_chunk_length:
            current_chunk += word + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = word + " "
    chunks.append(current_chunk.strip())
    print("there are {} chunks".format(len(chunks)))
    return chunks

def generate_summary(text_chunks):
    summary = ""
    counter = 0
    for chunk in text_chunks:
        print("summarizing chunk ", counter)
        inputs = tokenizer.encode(chunk, return_tensors='pt', truncation=True)
        summary_ids = model.generate(inputs, max_new_tokens=16384, min_length=40, length_penalty=3.0, num_beams=6)
        chunk_summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        summary += chunk_summary + " "
        print(summary)
        counter += 1
    return summary

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.get_json()
    url = data['url']
    
    # insert code here

    transcript = ""
    return jsonify({'transcript': transcript})

def applyWhisper() -> str:
    # Example YouTube link: 'https://www.youtube.com/watch?v=f60dheI4ARg'
    
    data = request.get_json()
    url = data['url']
    
    yt = YouTube(url)
    video = yt.streams.filter(only_audio=True).first()
    destination = '.'
    out_file = video.download(output_path=destination)
    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    os.rename(out_file, new_file)
    
    model = whisper.load_model("tiny")  # Options: small, medium, large, etc.
    result = model.transcribe(new_file)
    transcript = result["text"]
    
    return jsonify({'transcript': transcript})
    

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    transcript = data['transcript']
    # print("Received transcript:", transcript)

    # Remove stopwords from the input text
    transcript = remove_stopwords(transcript)

    max_chunk_length = 500  # Adjust the chunk length as needed
    text_chunks = split_text(transcript, max_chunk_length)
    
    # Generate summary for the text chunks
    summary = generate_summary(text_chunks)
    print(summary)
    return jsonify({'summary': summary})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
