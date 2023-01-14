# LED Strip
from led_animation_seq import LedStripAnimationSeq
LED_STRIP_PIN = 12
LED_STRIP_COUNT = 20

# LED Strip Animation
led_strip_seq = None
animation_seq = [
    ['blink', 5000],
    ['move_up_with_tail', 5000, {"speed": 50, "active_count": 1, "colors": (100, 100, 100)}],
    ['move_down_with_tail', 5000, {"speed": 50, "active_count": 1, "colors": (100, 100, 100)}],
    ['none', 5000, {"active_count": 1, "colors": (100, 100, 100)}],
]

def change_animation_callback(next_seq_index):
    print(f"change animation, number {next_seq_index}")
    # return to overriding the sequence step so that the animation will jump to the one you want
    # None will go to next animation
    if (next_seq_index == 2):
        return 3

def seq_end_callback():
    print(f"sequence end")
    # return to overriding the sequence step so that the animation will jump to the one you want
    # None will go to next animation
    return 1    

seq_callbacks = {
    "change_animation": change_animation_callback,
    "seq_end": seq_end_callback,
    }

# functions
def init_setup():
    global led_strip_seq
    led_strip_seq = LedStripAnimationSeq(LED_STRIP_PIN,
                                         LED_STRIP_COUNT,
                                         animation_seq,
                                         seq_callbacks = seq_callbacks)

def main_loop():
    global led_strip_seq
    led_strip_seq.check_event()


# main program start
init_setup()
while True:
    main_loop()
    



