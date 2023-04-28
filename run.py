from psychtoolbox import WaitSecs
from functions import *
from events import EventMarker

# --- Constants ---
FREQS = [200, 220, 240, 260, 280, 300, 320, 340, 360, 380, 400]
TONE_DUR = 0.2
N_PRACTICE_TRIALS = 3
N_TRIALS = 50

# --- Task ---

SUB_NUM = input('Input subject number: ')

#KB = get_keyboard('Dell Dell USB Entry Keyboard')
WIN = get_window()
seed = set_seed(SUB_NUM)

LOG = open_log(SUB_NUM)
points = get_points(LOG)
trial_num = get_trial_num(LOG)


if trial_num < 2:
    instructions(WIN)
    practice_trial_num = 1
    while practice_trial_num <= N_PRACTICE_TRIALS:
        practice_ready(WIN, practice_trial_num)
        freq = play_target(WIN, FREQS, TONE_DUR)
        WaitSecs(0.5)
        white_noise(1)
        WaitSecs(0.5)
        displaced_freq = play_displaced_target(WIN, TONE_DUR, freq)
        response = pitch_adjustment(WIN, TONE_DUR, displaced_freq)
        WaitSecs(0.5)
        practice_feedback(WIN, freq, response, points)
        practice_trial_num += 1


start_block(WIN)
while trial_num <= N_TRIALS:
    print(f'trial_num: {trial_num}')
    ready(WIN, trial_num)
    freq = play_target(WIN, FREQS, TONE_DUR)
    WaitSecs(0.5)
    white_noise(1)
    WaitSecs(0.5)
    displaced_freq = play_displaced_target(WIN, TONE_DUR, freq)
    response = pitch_adjustment(WIN, TONE_DUR, displaced_freq)
    WaitSecs(0.5)
    diff, points = feedback( freq, response, points)
    write_log(LOG, seed, SUB_NUM, trial_num, freq, displaced_freq, response, diff, points)
    trial_num += 1


end(WIN, points)

print("Block over :-)")
core.quit()
