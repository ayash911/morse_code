from flask import Flask, request, render_template, send_file, abort
from pydub import AudioSegment
import numpy as np
import logging
import os
import uuid

app = Flask(__name__)

# Create a directory to store audio files
AUDIO_DIRECTORY = 'tmp'  # Directory to store generated audio files
os.makedirs(AUDIO_DIRECTORY, exist_ok=True)

# Load Morse code mappings
morse_code_dict = {}
with open('morse_code.txt', 'r') as file:
    for line in file:
        char, code = line.strip().split('   ')
        morse_code_dict[char] = code

# Convert text to Morse code
def convert_to_morse(text):
    return ' '.join(morse_code_dict[char] for char in text.lower() if char in morse_code_dict)

# Generate a sine wave for the given frequency and duration
def generate_sine_wave(frequency, duration, sample_rate=44100):
    t = np.linspace(0, duration / 1000, int(sample_rate * duration / 1000), endpoint=False)
    wave = 0.5 * np.sin(2 * np.pi * frequency * t)
    audio_data = np.int16(wave * 32767)
    return AudioSegment(audio_data.tobytes(), frame_rate=sample_rate, sample_width=2, channels=1)

# Generate Morse code audio from the Morse code string
def generate_morse_audio(morse_code):
    audio = AudioSegment.silent(duration=0)
    for symbol in morse_code:
        if symbol == '.':
            beep = generate_sine_wave(frequency=1000, duration=100)
            audio += beep + AudioSegment.silent(duration=100)
        elif symbol == '-':
            beep = generate_sine_wave(frequency=1000, duration=300)
            audio += beep + AudioSegment.silent(duration=100)
        else:
            audio += AudioSegment.silent(duration=200)  # Unique filename
    # filename = os.path.join(AUDIO_DIRECTORY, f'{uuid.uuid4()}.wav')  # Unique filename
    filename = f'tmp\{uuid.uuid4()}.wav'
    audio.export(filename, format='wav')
    return filename

# Home route for rendering the input form and displaying Morse code
@app.route('/', methods=['GET', 'POST'])
def home():
    morse_code = ''
    input_text = ''
    audio_file_path = ''
    if request.method == 'POST':
        input_text = request.form['text']
        morse_code = convert_to_morse(input_text)
        audio_file_path = generate_morse_audio(morse_code)
    return render_template('index.html', input_text=input_text, morse_code=morse_code, audio_file=audio_file_path)

# Route to play the generated audio
@app.route('/play/<path:filename>')
def play_audio(filename):
    filepath = filename  # Update the path
    if not os.path.isfile(filepath):
        logging.error(f"File not found: {filepath}")
        return abort(404, description="File not found")
    return send_file(filepath, mimetype='audio/wav')

if __name__ == '__main__':
    app.run(debug=True)
