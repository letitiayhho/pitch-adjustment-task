from psychopy import prefs
prefs.hardware['audioLib'] = ['ptb']
from psychopy.sound.backend_ptb import SoundPTB as Sound
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors
from psychtoolbox import GetSecs, WaitSecs, hid
from psychopy.hardware.keyboard import Keyboard
import random
#import time
import numpy as np
from scipy.stats import beta
import os
import git
import pandas as pd


def get_window():
    #WIN = visual.Window(size = (1920, 1080),
    WIN = visual.Window(size = (800, 600),
    screen = -1,
    units = "norm",
    fullscr = False,
    pos = (0, 0),
    allowGUI = False)
    return(WIN)

def open_log(SUB_NUM):
    log = "data/logs/sub-" + SUB_NUM + ".log"

    if not os.path.isfile(log): # create log file if it doesn't exist
        print(f"Creating {log}")
        d = {
            'sub_num': [],
            'block': [],
            'trial_num': [],
            'tone_num': [],
            'freq': [],
            'displaced_freq': [],
            'response': [],
            }
        print(d)
        df = pd.DataFrame(data = d)
        df.to_csv(log, mode='w', index = False)
    return(log)

def get_trial_num(LOG):
    log = pd.read_csv(LOG)
    trial_nums = log['trial_num']
    if len(trial_nums) == 0:
        trial_num = 1
    else:
        trial_num = trial_nums.iloc[-1] + 1
    trial_num = int(trial_num)
    return(trial_num)

def get_n_trials(block):
    if block == 0:
        n_trials = 3
    else:
        n_trials = 20
    return(n_trials)

def start(WIN, block):
    if block == 0:
        instructions(WIN)
    else:
        block_welcome(WIN, block)

def display_instructions(WIN, text):
    instructions = visual.TextStim(WIN, text = text)
    instructions.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    WIN.flip()
    print(text)

def instructions(WIN):
    display_instructions(WIN, "Welcome to the experiment. \n \n  Press 'enter' to begin.")
    display_instructions(WIN, "At each trial you will be presented with a target tone. After the target you will hear a short burst of white noise followed by a pitch-adjusted version of the target tone. Please use the 'up' and 'down' arrow keys to adjust the pitch of the displaced tone until it matches the target tone then press 'enter' to submit your answer. \n \n  Press 'enter' to continue.")
    display_instructions(WIN, "You will now complete three practice trials. Please let you experimenter know if you have any questions or are experiencing any difficulties with the display or audio. \n \n Press 'enter' to continue to the practice trials.")

def block_welcome(WIN, block):
    display_instructions(WIN, f"Welcome to block number {block}/5. \n \n Press 'enter' to begin the block.")

def ready(WIN):
    block_begin = visual.TextStim(WIN, text = "Press 'enter' to begin!")
    block_begin.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    WIN.flip()

def get_freqs_from_pdf(a, b):
    x = np.arange(0, 1, 0.01)
    r = beta.rvs(a, b, size = 100)
    r = (r*950) + 50 # Stretch to 1000 Hz starting at 50 Hz
    r = np.round(r/10)* 10 # Round to nearest 10 Hz
    r = r.tolist()
    return(r)

def get_freq(freqs, block):
    if block == 0: # don't drop the freq during training
        freq = random.choice(freqs)
    freq = freqs.pop(random.randrange(len(freqs)))
    return(freq, freqs)

def play_target(WIN, TONE_DUR, freq):
    target_text = visual.TextStim(WIN, text = "Press 'space' to hear the target tone.")
    target_text.draw()
    WIN.flip()
    snd = Sound(freq, secs = TONE_DUR)

    while True:
        keys = event.getKeys(keyList = ['space'])
        if 'space' in keys:
            snd.play()
            WaitSecs(TONE_DUR)
            print('Target played')
            WIN.flip()
            break

def get_displaced_freq(freq):
    interval = random.randint(-10, 10)
    displacement = interval * freq * 0.02 # displace at intervals of 20% original tone
    displacement = round(displacement) # Round to nearest int
    displaced_freq = freq + displacement
    print(f'displaced_freq: {displaced_freq}')
    return(displaced_freq)

def play_tone(WIN, TONE_DUR, freq):
    WIN.flip()
    now = GetSecs()
    snd = Sound(freq, secs = TONE_DUR)
    prompt = visual.TextStim(WIN, '*')
    prompt.draw()
    snd.play()
    WIN.flip()
    WaitSecs(TONE_DUR)
    WIN.flip()

def white_noise(secs):
    start = random.uniform(0, 8)
    stop = start + secs + random.uniform(-0.1, 0.1)
    snd = Sound('gaussianwhitenoise.wav', startTime = start, stopTime = stop, volume = 0.5)
    snd.play()
    WaitSecs(stop - start)

def pitch_adjustment(WIN, TONE_DUR, freq, displaced_freq):
    play_tone(WIN, TONE_DUR, displaced_freq)

    keylist = ['up', 'down', 'return']
    interval = int(round(freq * 0.02))

    while True:
        keys = event.getKeys(keyList = keylist)
        if 'return' in keys: # empty response not accepted
            break
        elif keys:
            if 'up' in keys:
                displaced_freq += interval
                play_tone(WIN, TONE_DUR, displaced_freq)
            elif 'down' in keys:
                displaced_freq -= interval
                play_tone(WIN, TONE_DUR, displaced_freq)

    response = displaced_freq
    return(response)

def feedback(WIN, freq, response):
    display_instructions(WIN, f"Your answer was {response} Hz, the target was {freq} Hz.")

def broadcast(n_tones, var):
    if not isinstance(var, list):
        broadcasted_array = [var]*n_tones
    return(broadcasted_array)

def write_log(LOG, SUB_NUM, block, trial_num, freq, displaced_freq, response):
    print("Writing to log file")
    d = {
        'sub_num': SUB_NUM,
        'block': block,
        'trial_num': trial_num,
        'freq': freq,
        'displaced_freq': displaced_freq,
        'response': response,
        }
    df = pd.DataFrame(data = d,
            index = [trial_num])
    df.to_csv(LOG, mode='a', header = False, index = False)

def end(WIN, block):
    if block == 0:
        display_instructions(WIN, "Congratulations for finishing the practice block. Let your experimenter know if you have any questions or if you would like to repeat this practice block. If you are ready, you will now move on to the 5 experiment blocks, each of which will have 20 trials. \n \n Press 'enter' to complete this block.")
    else:
        display_instructions(WIN, f"End of block! You may now take a break if you wish. \n \n Press 'enter' to complete this block.")
