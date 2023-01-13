# LED Strip
import time
from led_animation_seq import LedStripAnimationSeq, add_led_strip_animation
LED_STRIP_PIN = 12
LED_STRIP_COUNT = 20

# LED Strip Animation
led_strip_seq = None
animation_seq = [
    ['blink_all', 5000],
    ['move_right_with_tail', 5000, {"speed": 50, "active_count": 1, "colors": (100, 100, 100)}],
    ['move_left_with_tail', 5000, {"speed": 50, "active_count": 1, "colors": (100, 100, 100)}],
    ['none', 5000, {"active_count": 1, "colors": (100, 100, 100)}],
]

led_strip_seq = LedStripAnimationSeq(LED_STRIP_PIN,
                                     LED_STRIP_COUNT,
                                     animation_seq,
                                     manual_trigger_event = True)

while (True):
    for i in range(10):
        time.sleep_ms(500)
        # trigger animation next step
        led_strip_seq.trigger_animation_event()
    time.sleep_ms(500)
    # trigger animation sequence event to change next animation
    led_strip_seq.next_animation()


