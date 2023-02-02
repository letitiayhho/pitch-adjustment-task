from psychtoolbox import WaitSecs
from functions import *
import random

# --- Constants ---
TONE_DUR = 0.25
WHITE_NOISE_DUR = 1
BLOCKS = 4
a, b = 2, 10 # Params for beta pdf for freqs

# --- Task ---

SUB_NUM = input('Input subject number: ')

random.seed(int(SUB_NUM))
WIN = get_window()
freqs = get_freqs_from_pdf(a, b)
LOG = open_log(SUB_NUM)
trial_num = get_trial_num(LOG)

for block in range(BLOCKS + 1):
    start(WIN, block)
    ready(WIN)
    n_trials = get_n_trials(block)
    while trial_num <= n_trials:
        print(f'trial_num: {trial_num}')
        freq, freqs = get_freq(freqs, block)
        play_target(WIN, TONE_DUR, freq)
        WaitSecs(np.random.uniform(0.3, 0.7))
        white_noise(WHITE_NOISE_DUR)
        WaitSecs(np.random.uniform(0.3, 0.7))
        displaced_freq = get_displaced_freq(freq)
        response = pitch_adjustment(WIN, TONE_DUR, freq, displaced_freq)
        WaitSecs(0.5)
        feedback(WIN, freq, response)
        print(displaced_freq)
        write_log(LOG, SUB_NUM, block, trial_num, freq, displaced_freq, response)
        trial_num += 1

    trial_num = 0
    end(WIN, block)

print("Block over :-)")
core.quit()
