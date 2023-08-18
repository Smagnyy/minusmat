import PySimpleGUI as sg
import wave
import json
import subprocess
import sys
import ffmpeg
from vosk import Model, KaldiRecognizer, SetLogLevel
import Word as custom_Word
from pydub import AudioSegment

list = ['бля', 'блят', 'бляд', 'сук', 'хуй', 'хуе', 'хуё', 'хуя', 'хую', 'хуи', 'пизд','ебл','ёбл', 'ебо', 'ёбо',
        'ебы', 'ёбы','ебу', 'ёбу','ебн','ёбн', 'еби', 'ёби', 'оеб','оёб','еба','ёба', 'гандон', 'гондон', 'долбоеб', 'долбоёб' ]

pristList = ['от', 'вы', 'за', 'про', 'у', 'на', 'пере', 'подъ', 'при', 'съ', 'до', 'вь', 'по', 'ни', 'а']

def MuteSound(start, end, ac):
    differ = (end - start) / 2
    start = start + differ / 5
    end = end - differ / 3
    print(start, end)

    before = ac[:int(start * 1000)]

    muted = ac[int(start * 1000):int(end * 1000)]
    backwards = muted.reverse()
    tss = AudioSegment.silent(duration=int(end * 1000) - int(start * 1000))

    after = ac[int(end * 1000):]
    res = before + tss + after
    return res

def OnlyMute(source, dest, name):
    audioClip = AudioSegment.from_file(source, format="mp3")
    file = open("1.txt", "r")

    result = audioClip

    for word in file:
        x = word.split()
        print(float(x[2]), float(x[5]))
        print(int(float(x[2]) * 1000), int(float(x[5]) * 1000))
        result = MuteSound(float(x[2]), float(x[5]), result)

    file.close()

    result.export(dest + name, format="mp3")
######################################################################################################

def Recogn( _INP, n_step):
    SAMPLE_RATE = 16000
    step = n_step
    inp = _INP
    # originalSound = inp.audio

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

    counter = 1

    flag = False
    with open("1.txt", "w") as file:
        for word in list_of_Words:
            if counter % step == 0:
                x = word.to_string().split()
                for filtr in list:
                    if flag:
                        flag = False
                        break
                    for attach in pristList:
                        if filtr in x[0] and attach in x[0] and x[0].find(attach) == 0 and x[0].find(filtr) - x[0].find(
                                attach) <= len(attach):
                            file.write(word.to_string() + '\n')
                            flag = True
                            print(x[0] + ' это оно первый иф')
                            break
                        elif filtr in x[0] and x[0].find(filtr) == 0:
                            file.write(word.to_string() + '\n')
                            flag = True
                            print(x[0] + ' это оно второй иф')
                            break
            counter += 1

######################################################################################################

sg.theme('Dark Grey 13')

layout = [[sg.Text('Source      '), sg.Input(enable_events= True, key = 'ss'), sg.FileBrowse(key = 'source',  file_types=(('MP3', '*.mp3'),))],
          [sg.Text('Destination'), sg.Input(enable_events= True,key = 'dest'), sg.FolderBrowse(key = 'browse0')],
          [sg.Radio('Full', "RADIO1", default=True), sg.Radio('Recognize only', "RADIO1"), sg.Radio('Mute only', "RADIO1")],
          [sg.Text('Step'), sg.Spin([i for i in range(1,50)], initial_value=1)],
          [sg.Text('Progress'), sg.ProgressBar(1000, orientation='h', size=(20, 20), key='progressbar'), sg.Text('', key = 'etap')],
          [sg.OK(key = 'ok', disabled= True), sg.Cancel(), ]]

window = sg.Window('Minusmat', layout)

f_name = ''
pathTo = ''

while True:                             # The Event Loop
    event, values = window.read()

    # print(event, values) #debug
    if event in (None, 'Exit', 'Cancel'):
        break
    elif event == 'ok':
        print(event, values)
        if values[0]:
            window['etap'].update('1/2')
            Recogn(values['ss'], values[3])
            window['etap'].update('2/2')
            OnlyMute(values['ss'], values['dest'], f_name)
            window['etap'].update('Done')
        elif values[1]:
            window['etap'].update('1/1')
            Recogn(values['ss'], values[3])
            window['etap'].update('Done')
        elif values[2]:
            window['etap'].update('1/1')
            OnlyMute(values['ss'], values['dest'], f_name)
            window['etap'].update('Done')



    if event == 'ss':
        pos = values['ss'].rfind('/')
        print(pos)
        f_name = "/[MUTED] " + values['ss'][pos+1:]
        pathTo = values['ss'][:pos]
        print(f_name, pathTo)
        window['dest'].update(value = pathTo)
        window['ok'].update(disabled=False)


