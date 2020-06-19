"""PyAudio Example: Play a wave file (callback version)."""

import pyaudio
import wave
import time
import sys
import numpy as np
import matplotlib.pyplot as plt
import wavio

plt.style.use('ggplot')

if len(sys.argv) < 2:
    print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
    sys.exit(-1)

wf = wave.open(sys.argv[1], 'rb')
fs = wf.getframerate()
channels = wf.getnchannels()
bytes_per_sample = wf.getsampwidth()
print(wf.getframerate())
# instantiate PyAudio (1)
p = pyaudio.PyAudio()

global sub_bass_max, bass_max, low_midrange_max, midrange_max, upper_midrange_max, presence_max, brilliance_max
global sub_bass_beat, bass_beat, low_midrange_beat, midrange_beat, upper_midrange_beat, presence_beat, brilliance_beat
sub_bass_max = 10
bass_max = 10
low_midrange_max = 10
midrange_max = 10
upper_midrange_max = 10
presence_max = 10
brilliance_max = 10
sub_bass_beat = False
bass_beat = False
low_midrange_beat = False
midrange_beat = False
upper_midrange_beat = False
presence_beat = False
brilliance_beat = False


# Beat Detection Algo
def beat_detect(in_data):
    audio = wavio._wav2array(channels, bytes_per_sample, in_data)

    audio_fft = np.abs((np.fft.fft(audio)[0:int(len(audio)/2)])/len(audio))
    freqs = fs*np.arange(len(audio)/2)/len(audio)
    
    # Frequency Ranges for each important audio group
    sub_bass_indices = [idx for idx,val in enumerate(freqs) if val >= 20 and val <= 60]
    bass_indices = [idx for idx,val in enumerate(freqs) if val >= 60 and val <= 250]
    low_midrange_indices = [idx for idx,val in enumerate(freqs) if val >= 250 and val <= 500]
    midrange_indices = [idx for idx,val in enumerate(freqs) if val >= 500 and val <= 2000]
    upper_midrange_indices = [idx for idx,val in enumerate(freqs) if val >= 2000 and val <= 4000]
    presence_indices = [idx for idx,val in enumerate(freqs) if val >= 4000 and val <= 6000]
    brilliance_indices = [idx for idx,val in enumerate(freqs) if val >= 6000 and val <= 20000]

    # print(audio_fft[sub_bass_indices])
    sub_bass = np.max(audio_fft[sub_bass_indices])
    bass = np.max(audio_fft[bass_indices])
    low_midrange = np.max(audio_fft[low_midrange_indices])
    midrange = np.max(audio_fft[midrange_indices])
    upper_midrange = np.max(audio_fft[upper_midrange_indices])
    presence = np.max(audio_fft[presence_indices])
    brilliance = np.max(audio_fft[brilliance_indices])

    global sub_bass_max, bass_max, low_midrange_max, midrange_max, upper_midrange_max, presence_max, brilliance_max
    global sub_bass_beat, bass_beat, low_midrange_beat, midrange_beat, upper_midrange_beat, presence_beat, brilliance_beat
    sub_bass_max = max(sub_bass_max, sub_bass)
    # print("Max:", sub_bass_max)
    # print("Bass:", sub_bass)

    bass_max = max(bass_max, bass)
    low_midrange_max = max(low_midrange_max, low_midrange)
    midrange_max = max(midrange_max, midrange)
    upper_midrange_max = max(upper_midrange_max, upper_midrange)
    presence_max = max(presence_max, presence)
    brilliance_max = max(brilliance_max, brilliance)

    if sub_bass >= sub_bass_max*.9 and not sub_bass_beat:
        sub_bass_beat = True
        print("Sub Bass Beat")
    elif sub_bass < sub_bass_max*.3:
        sub_bass_beat = False

    if bass >= bass_max*.9 and not bass_beat:
        bass_beat = True
        print("Bass Beat")
    elif bass < bass_max*.3:
        bass_beat = False

    if low_midrange >= low_midrange_max*.9 and not low_midrange_beat:
        low_midrange_beat = True
        print("Low Midrange Beat")
    elif low_midrange < low_midrange_max*.3:
        low_midrange_beat = False

    if midrange >= midrange_max*.9 and not midrange_beat:
        midrange_beat = True
        print("Midrange Beat")
    elif midrange >= midrange_max*.3:
        midrange_beat = False

    if upper_midrange >= upper_midrange_max*.9 and not upper_midrange_beat:
        upper_midrange_beat = True
        print("Upper Midrange Beat")
    elif upper_midrange < upper_midrange_max*.3:
        upper_midrange_beat = False

    if presence >= presence_max*.9 and not presence_beat:
        presence_beat = True
        print("Presence Beat")
    elif presence < presence_max*.3:
        presence_beat = False

    if brilliance >= brilliance_max*.9 and not brilliance_beat:
        brilliance_beat = True
        print("Brilliance Beat")
    elif brilliance < brilliance_max*.3:
        brilliance_beat = False

    primary_freq = freqs[np.argmax(audio_fft)]
    # print("Primary Frequency: ", primary_freq)


# define callback (2)
def callback(in_data, frame_count, time_info, status):
    data = wf.readframes(frame_count)
    beat_detect(data)
    return (data, pyaudio.paContinue)

# open stream using callback (3)
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
                stream_callback=callback)

# start the stream (4)
stream.start_stream()

# wait for stream to finish (5)
while stream.is_active():
    time.sleep(0.1)

# stop stream (6)
stream.stop_stream()
stream.close()
wf.close()

# close PyAudio (7)
p.terminate()