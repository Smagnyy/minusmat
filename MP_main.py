#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8

import wave
import json
import sys
import Word as custom_Word
import ffmpeg
from multiprocessing.dummy import Pool
from vosk import Model, KaldiRecognizer

list = ['бля', 'блят', 'бляд', 'сук', 'хуй', 'хуе', 'хуё', 'хуя', 'хую', 'хуи', 'пизд','ебл','ёбл',
        'ебы', 'ёбы','ебу', 'ёбу','ебн','ёбн', 'еби', 'ёби', 'оеб','оёб','еба','ёба', 'гандон', 'гондон' ]

pristList = ['от', 'вы', 'за', 'про', 'у', 'на', 'пере', 'подъ', 'при', 'съ', 'до', 'вь', 'по', 'ни', 'а']

SAMPLE_RATE = 16000
model = Model("vosk-model-ru-0.22")

def recognize(line):

    audio_filename = (
        ffmpeg.input(str(line) + '.mp3').output(str(line) +'.wav', format='wav', acodec='pcm_s16le', ac=1, ar='16k').overwrite_output().run()
    )
    wf = wave.open(str(line+1)+'.wav', "rb")
    rec = KaldiRecognizer(model, SAMPLE_RATE)
    rec.SetWords(True)

    results = []

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            part_result = json.loads(rec.Result())
            results.append(part_result)
    part_result = json.loads(rec.FinalResult())
    results.append(part_result)
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

    flag = False
    with open(str(line) +".txt", "w") as file:
        for word in list_of_Words:
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

    # output to the screen
    for word in list_of_Words:
        print(word.to_string())


