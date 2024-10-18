from flask import Flask, request, render_template, send_file, abort
from pydub import AudioSegment
import numpy as np
import tempfile
import os

app = Flask(__name__)

morse_code_dict = {}
with open('morse_code.txt', 'r') as file:
    for line in file:
        char, code = line.strip().split('   ')
        morse_code_dict[char] = code

def convert_to_morse(text):
    return ' '.join(morse_code_dict[char] for char in text.lower() if char in morse_code_dict)

def generate_sine_wave(frequency, duration, sample_rate=44100):
    t = np.linspace(0, duration / 1000, int(sample_rate * duration / 1000), endpoint=False)
    wave = 0.5 * np.sin(2 * np.pi * frequency * t)
    audio_data = np.int16(wave * 32767)
    return AudioSegment(audio_data.tobytes(), frame_rate=sample_rate, sample_width=2, channels=1)

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
            audio += AudioSegment.silent(duration=200)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
        audio.export(tmp_file.name, format='wav')
        return tmp_file.name

@app.route('/', methods=['GET', 'POST'])
def home():
    morse_code = ''
    input_text = ''
    audio_file_path = ''
    if request.method == 'POST':
        input_text = request.form['text']
        morse_code = convert_to_morse(input_text)
        audio_file_path = generate_morse_audio(morse_code)
        print(f"Generated audio file at: {audio_file_path}")
    return render_template('index.html', input_text=input_text, morse_code=morse_code, audio_file=audio_file_path)

@app.route('/play/<path:filename>')
def play_audio(filename):
    if not os.path.isfile(filename):
        return abort(404, description="File not found")
    return send_file(filename, mimetype='audio/wav')

if __name__ == '__main__':
    app.run(debug=True)
