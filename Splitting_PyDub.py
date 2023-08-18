import sys
from pydub import AudioSegment

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
    res = before + backwards + after
    return res

audioClip = AudioSegment.from_file(sys.argv[1], format="mp3")
file = open("1.txt", "r")

result = audioClip



for word in file:
    x = word.split()
    print(float(x[2]), float(x[5]))
    print(int(float(x[2])*1000), int(float(x[5])*1000))
    result = MuteSound(float(x[2]), float(x[5]), result)


file.close()

result.export("result.mp3", format="mp3")