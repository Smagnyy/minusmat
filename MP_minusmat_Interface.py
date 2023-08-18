import PySimpleGUI as sg
import wave
import json
import subprocess
import sys
import ffmpeg
from vosk import Model, KaldiRecognizer, SetLogLevel
import Word as custom_Word
from pydub import AudioSegment
import multiprocessing as mp


import os

from multiprocessing.dummy import Pool
from multiprocessing import Pool

list = ['бля', 'блят', 'бляд', 'сук', 'хуй', 'хуе', 'хуё', 'хуя', 'хую', 'хуи', 'пизд','ебл','ёбл', 'ебо', 'ёбо',
        'ебы', 'ёбы','ебу', 'ёбу','ебн','ёбн', 'еби', 'ёби', 'оеб','оёб','еба','ёба', 'гандон', 'гондон', 'долбоеб', 'долбоёб' ]

pristList = ['от', 'вы', 'за', 'про', 'у', 'на', 'пере', 'подъ', 'при', 'съ', 'до', 'вь', 'по', 'ни', 'а']

step = 1
count_t = 3

def SplitMP3(countOfProcs, source, dest):
    audioClip = AudioSegment.from_file(source, format="mp3")
    count = 1
    dur = audioClip.duration_seconds
    print(dur)
    step = dur/ countOfProcs
    print (step)
    #print( str(count) + '.mp3') #dest + '/' +
    while count <= countOfProcs:
        result = audioClip[:step*1000]
        audioClip = audioClip[step * 1000:]
        result.export(str(count) + '.mp3', format="mp3") #dest +  '/' +
        count += 1


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

def OnlyMute(numbOfProc): #dest,
    audioClip = AudioSegment.from_file(str(numbOfProc)+'.mp3', format="mp3") #dest+'/'+
    file = open(str(numbOfProc)+".txt", "r")

    result = audioClip

    for word in file:
        x = word.split()
        print(float(x[2]), float(x[5]))
        print(int(float(x[2]) * 1000), int(float(x[5]) * 1000))
        result = MuteSound(float(x[2]), float(x[5]), result)

    file.close()

    result.export('[MUTED]'+str(numbOfProc)+'.mp3', format="mp3") #dest+'/[MUTED]'+

def Combine(numbOfProc, dest, name):

    comb = AudioSegment.empty()
    n = 1
    while n <= numbOfProc:
        newAC = AudioSegment.from_file('[MUTED]'+str(n)+'.mp3', format="mp3")
        comb = comb + newAC
        n+=1

    comb.export(dest + name, format="mp3") #dest+'/[MUTED]'+
######################################################################################################

def Recogn(numbOfProc): #_INP, n_step
    SAMPLE_RATE = 16000
    #step = n_step
    #inp = _INP
    inp = str(numbOfProc)+'.mp3'
    print(inp)
    # originalSound = inp.audio

    audio_filename = (
        ffmpeg.input(inp).output(str(numbOfProc)+'.wav', format='wav', acodec='pcm_s16le', ac=1, ar='16k').overwrite_output().run()
    )

    wf = wave.open(str(numbOfProc)+'.wav', "rb")

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
    with open(str(numbOfProc)+".txt", "w") as file:
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
if __name__ == '__main__':
    sg.theme('Dark Grey 13')

    layout = [[sg.Text('Source      '), sg.Input(enable_events= True, key = 'ss'), sg.FileBrowse(key = 'source',  file_types=(('MP3', '*.mp3'),))],
            [sg.Text('Destination'), sg.Input(enable_events= True,key = 'dest'), sg.FolderBrowse(key = 'browse0')],
            [sg.Radio('Full', "RADIO1", default=True), sg.Radio('Recognize only', "RADIO1"), sg.Radio('Mute only', "RADIO1")],
            [sg.Text('Step'), sg.Spin([i for i in range(1,50)], initial_value=1), sg.Text('Threads'), sg.Spin([i for i in range(1,50)], initial_value=count_t)],
            [sg.OK(key = 'ok', disabled= True)]]

    window = sg.Window('Minusmat', layout)

    f_name = ''
    pathTo = ''

    while True:                             # The Event Loop
        event, values = window.read()

        # print(event, values) #debug
        if event in (None, 'Exit', 'Cancel'):
            break
        elif event == 'ok':
            step = values[3]
            count_t = values[4]
            print(event, values)
            if values[0]:
                print("Splitting...")
                SplitMP3(count_t, values['ss'], values['dest'])
                print("DONE! Recognizing...")
                #Recogn(values['ss'], values[3])
                with Pool(count_t) as p:
                    p.map(Recogn, range(1, count_t + 1))
                print('DONE! Muting...')
                #OnlyMute(values['ss'], values['dest'], f_name)
                with Pool(count_t) as p:
                    p.map(OnlyMute, range(1, count_t + 1))
                print('DONE! Combining...')
                Combine(count_t, values['dest'], f_name)
                print('DONE!')
            elif values[1]:
                print("Splitting...")
                SplitMP3(count_t, values['ss'], values['dest'])
                print("DONE! Recognizing...")
                with Pool(count_t) as p:
                    p.map(Recogn, range(1, count_t + 1))
                print("DONE!")
                # Recogn(values['dest'] + '/' + str(n) + '.mp3', values[3])
                #n = 1
                #procs = []
                #SplitMP3(count_t, values['ss'], values['dest'])
                #while n <= count_t:
                    #proc = mp.Process(target = Recogn, args = (values['dest'], values[3], n))
                    #procs.append(proc)
                    #proc.start()
                    #n += 1
                #for proc in procs:
                    #proc.join()
            elif values[2]:
                with Pool(count_t) as p:
                    p.map(OnlyMute, range(1, count_t + 1))
                print("DONE! Combining...")
                Combine(count_t, values['dest'], f_name)
                print("DONE!")
                #n = 1
                #procs = []
                #print(values['dest']+ '/' + str(n) + '.mp3')
                #while n <= count_t:
                #    proc = mp.Process(target = OnlyMute, args = (values['dest'], n))
                #    procs.append(proc)
                #    print('1')
                #    print(proc.name)
                #    proc.start()
                #    n += 1
                    #for proc in procs:
                        #proc.join()
                #OnlyMute(values['ss'], values['dest'], f_name)

        if event == 'ss':
            pos = values['ss'].rfind('/')
            print(pos)
            f_name = "/[MUTED] " + values['ss'][pos+1:]
            pathTo = values['ss'][:pos]
            print(f_name, pathTo)
            window['dest'].update(value = pathTo)
            window['ok'].update(disabled=False)


