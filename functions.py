from psychopy import prefs
prefs.hardware['audioLib'] = ['ptb']
from psychopy.sound.backend_ptb import SoundPTB as Sound
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors
from psychtoolbox import GetSecs, WaitSecs, hid
from psychopy.hardware.keyboard import Keyboard
import random
#import time
import os
import git
import pandas as pd

def get_window():
    #WIN = visual.Window(size = (1920, 1080),
    WIN = visual.Window(size = (600, 400),
    screen = -1,
    units = "norm",
    fullscr = False,
    pos = (0, 0),
    allowGUI = False)
    return(WIN)

def get_keyboard(dev_name):
    devs = hid.get_keyboard_indices()
    idxs = devs[0]
    names = devs[1]
    try:
        idx = [idxs[i] for i, nm in enumerate(names) if nm == dev_name][0]
    except:
        raise Exception(
        'Cannot find %s! Available devices are %s.'%(dev_name, ', '.join(names))
        )
    return Keyboard(idx)

def open_log(SUB_NUM):
    log = "data/logs/sub-" + SUB_NUM + ".log"

    if not os.path.isfile(log): # create log file if it doesn't exist
        print(f"Creating {log}")
        d = {
            'seed': [],
            'sub_num': [],
            'trial_num': [],
            'freq': [],
            'displaced_freq': [],
            'response': [],
            'diff': [],
            'points': [],
            }
        print(d)
        df = pd.DataFrame(data = d)
        df.to_csv(log, mode='w', index = False)
    return(log)

def get_points(LOG):
    log = pd.read_csv(LOG)
    points = log['points']
    if len(points) == 0:
        points = 0
    else:
        points = points.iloc[-1]
    points = float(points)
    print(f'points: {points}')
    return(points)

def get_trial_num(LOG):
    log = pd.read_csv(LOG)
    trial_nums = log['trial_num']
    if len(trial_nums) == 0:
        trial_num = 1
    else:
        trial_num = trial_nums.iloc[-1] + 1
    trial_num = int(trial_num)
    print(f"trial_num: {trial_num}")
    return(trial_num)

def display_instructions(WIN, text):
    instructions = visual.TextStim(WIN, text = text)
    instructions.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    WIN.flip()
    print(text)

def instructions(WIN):
    display_instructions(WIN, "Welcome to the experiment. \n \n  Press 'enter' to begin.")
    display_instructions(WIN, "In each trial you will be asked to listen to a target tone. After the target tone a burst of white noise will play. Following the white noise, a pitch-adjusted version of the original target tone will play. Your job is to use the up and down arrow keys to adjust the pitch of this tone until it matches that of the original target tone. Press 'enter' to submit your answer.\n \n Press 'enter' to continue.")
    display_instructions(WIN, "You will now complete three practice trials. Please let you experimenter know if you have any questions or are experiencing any difficulties with the display, audio quality, or audio volume. \n \n Press 'enter' to continue to the practice trials.")

def start_block(WIN):
    display_instructions(WIN, "Congratulations for completing the practice trials. For the following experiment trials you will receive 2 points for every tone you accurately match with its target and 1 point if you are close enough. There are 50 trials in total. You will not receive feedback for these trials. You will receive your score at the end of all the trials. \n \n Press 'enter' to continue to the experiment trials.")

def practice_ready(WIN, trial_num):
    display_instructions(WIN, f"Practice trial {trial_num}/3. \n \n Press 'enter' to hear the target tone and begin the trial.")

def ready(WIN, trial_num):
    display_instructions(WIN, f"Trial {trial_num}/50. \n \n Press 'enter' to hear the target tone and begin the trial.")

def set_seed(SUB_NUM):
    seed = int(SUB_NUM)
    print("Current seed: " + str(seed))
    random.seed(seed)
    return(seed)

def fixation(WIN, secs):
    fixation = visual.TextStim(WIN, '+')
    fixation.draw()
    WIN.flip()
    jitter = random.uniform(-0.1, 0.1)
    WaitSecs(secs + jitter)
    WIN.flip()
    return(fixation)

def play_target(WIN, FREQS, TONE_DUR):
    # Pick target freq
    index = random.randint(0, 1)
    freq = FREQS[index]
    print(f'freq: {freq}')

    now = GetSecs()
    snd = Sound(freq, secs = TONE_DUR)
    prompt = visual.TextStim(WIN, '*')
    prompt.draw()
    snd.play(when = now + 0.001)
    WaitSecs(0.001)
#    start = time.time()
    WIN.flip()
    WaitSecs(TONE_DUR)
    WIN.flip()
#    end = time.time()
#    print(f"tone len: {end-start}")
    return(freq)

def display_cue_only(WIN, TONE_DUR):
    now = GetSecs()
    prompt = visual.TextStim(WIN, '*')
    prompt.draw()
    WaitSecs(0.001)
    WIN.flip()
    WaitSecs(TONE_DUR)
    WIN.flip()

def play_adjusted_tone(WIN, TONE_DUR, freq):
    WIN.flip()
    now = GetSecs()
    snd = Sound(freq, secs = TONE_DUR)
    prompt = visual.TextStim(WIN, '*')
    prompt.draw()
    snd.play(when = now + 0.001)
    WIN.flip()
    WaitSecs(TONE_DUR)
    WIN.flip()

def white_noise(secs):
    start = random.uniform(0, 8)
    stop = start + secs + random.uniform(-0.1, 0.1)
    snd = Sound('pitch-adjustment/gaussianwhitenoise.wav', startTime = start, stopTime = stop, volume = 0.4)
    snd.play()
    WaitSecs(stop - start)

def play_displaced_target(WIN, TONE_DUR, freq):
    displacement = random.randint(-10, 10)
    displaced_freq = freq + displacement
    play_adjusted_tone(WIN, TONE_DUR, displaced_freq)
    print(f'displaced_freq: {displaced_freq}')
    return(displaced_freq)

def pitch_adjustment(WIN, TONE_DUR, displaced_freq):
    keylist = ['up', 'down', 'return']

    while True:
        keys = event.getKeys(keyList = keylist)
        if 'return' in keys: # empty response not accepted
            break
        elif keys:
            if 'up' in keys:
                displaced_freq += 1
                play_adjusted_tone(WIN, TONE_DUR, displaced_freq)
            elif 'down' in keys:
                displaced_freq -= 1
                play_adjusted_tone(WIN, TONE_DUR, displaced_freq)

    response = displaced_freq
    print(f"response: {response}")
    return(response)

def practice_feedback(WIN, freq, response, points):
    diff = response - freq
    if diff == 0:
        points += 2
        feedback = f"Spot on! \n \n Press 'enter' to continue."
    elif abs(diff) < 3:
        points += 1
        feedback = f"Close enough! You were {abs(diff)} Hz above the target. \n \n Press 'enter' to continue."
    elif diff >= 3:
        feedback = f"You were {abs(diff)} Hz above the target. \n \n Press 'enter' to continue."
    elif diff <= 3:
        feedback = f"You were {abs(diff)} Hz below the target. \n \n Press 'enter' to continue."

    display_instructions(WIN, feedback)

def feedback(freq, response, points):
    diff = response - freq
    if diff == 0:
        points += 2
        #feedback = f"Spot on! You now have {points} points. You just completed trial {trial_num}/50. Press 'enter' to continue."
    elif abs(diff) < 3:
        points += 1
        #feedback = f"Close enough! You were {abs(diff)} Hz above the target. You now have {points} points. You just completed trial {trial_num}/50. Press 'enter' to continue."
    #elif abs(diff) >= 3:
        #feedback = f"You were {abs(diff)} Hz above the target. You just completed trial {trial_num}/50. Press 'enter' to continue."
    #display_instructions(WIN, feedback)
    print(f"points: {points}")
    return(diff, points)

def broadcast(n_tones, var):
    if not isinstance(var, list):
        broadcasted_array = [var]*n_tones
    return(broadcasted_array)

def write_log(LOG, seed, SUB_NUM, trial_num, freq, displaced_freq, response, diff, points):
    print("Writing to log file")
    d = {
        'seed': seed,
        'sub_num': SUB_NUM,
        'trial_num': trial_num,
        'freq': freq,
        'displaced_freq': displaced_freq,
        'response': response,
        'diff': diff,
        'points': points
        }
    df = pd.DataFrame(data = d, index = [0])
    df.to_csv(LOG, mode='a', header = False, index = False)

def end(WIN, points):
    display_instructions(WIN, f"Congratulations! This task is now over. You earned a total of {points}. Your experimenter will now come and check on you. \n \n Press 'enter' to end the experiment.")
