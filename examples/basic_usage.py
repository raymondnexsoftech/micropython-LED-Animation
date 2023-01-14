# LED Strip
from led_animation_seq import LedStripAnimationSeq
LED_STRIP_PIN = 12
LED_STRIP_COUNT = 20

# LED Strip Animation
led_strip_seq = None
animation_seq = [
    ['blink_all', 5000],
    ['move_up_with_tail', 5000, {"speed": 50, "active_count": 1, "colors": (100, 100, 100)}],
    ['move_down_with_tail', 5000, {"speed": 50, "active_count": 1, "colors": (100, 100, 100)}],
    ['none', 5000, {"active_count": 1, "colors": (100, 100, 100)}],
]

# functions
def init_setup():
    global led_strip_seq
    led_strip_seq = LedStripAnimationSeq(LED_STRIP_PIN,
                                         LED_STRIP_COUNT,
                                         animation_seq)

def main_loop():
    global led_strip_seq
    led_strip_seq.check_event()


# main program start
init_setup()
while True:
    main_loop()
    


