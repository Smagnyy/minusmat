import wave
import json
import subprocess
import sys
import ffmpeg
from vosk import Model, KaldiRecognizer, SetLogLevel
import Word as custom_Word


list = ['бля', 'блят', 'бляд', 'сук', 'хуй', 'хуе', 'хуё', 'хуя', 'хую', 'хуи', 'пизд','ебл','ёбл',
        'ебы', 'ёбы','ебу', 'ёбу','ебн','ёбн', 'еби', 'ёби', 'оеб','оёб','еба','ёба', 'гандон', 'гондон' ]

SAMPLE_RATE = 16000

inp = sys.argv[1]
#originalSound = inp.audio


audio_filename = (
    ffmpeg.input(inp).output('1.wav', format='wav', acodec='pcm_s16le', ac=1, ar='16k').overwrite_output().run()
)
wf = wave.open('1.wav', "rb")

print('start')

model_path = "vosk-model-ru-0.22"
model = Model(model_path)

rec = KaldiRecognizer(model, SAMPLE_RATE)
rec.SetWords(True)




# get the list of JSON dictionaries
results = []
# recognize speech using vosk model
while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        part_result = json.loads(rec.Result())
        results.append(part_result)
part_result = json.loads(rec.FinalResult())
results.append(part_result)

# convert list of JSON dictionaries to list of 'Word' objects
list_of_Words = []
for sentence in results:
    if len(sentence) == 1:
        # sometimes there are bugs in recognition
        # and it returns an empty dictionary
        # {'text': ''}
        continue
    for obj in sentence['result']:
        w = custom_Word.Word(obj)  # create custom Word object
        list_of_Words.append(w)  # and add it to list

wf.close()  # close audiofile

with open("1.txt", "w") as file:
    for word in list_of_Words:
        x = word.to_string().split()
        for filtr in list:
            if filtr in x[0]:
                file.write(word.to_string() + '\n')
                break

# output to the screen
for word in list_of_Words:
    print(word.to_string())