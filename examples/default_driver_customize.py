# LED Strip
from machine import Pin
from led_animation_seq import LedStripAnimationSeq
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

def led_class_create(led_class, orig_callback, pin_number, led_count):
    # callback to create driver
    # return the created driver
    led_strip_pin = Pin(pin_number, Pin.OUT)
    return led_class(led_strip_pin, led_count, timing = (300, 900, 900, 300))

def led_class_fill(led_driver, orig_callback, value):
    # callback to fill all LEDs' buffer with same value
    # no return needed
    print("fill function called")
    orig_callback(value)            # skip the first two arguments, so only "value" need to pass

# functions
def init_setup():
    global led_strip_seq
    led_class_callbacks = {
        "create": led_class_create,
        "fill": led_class_fill,
    }

    led_strip_seq = LedStripAnimationSeq(LED_STRIP_PIN,
                                         LED_STRIP_COUNT,
                                         animation_seq,
                                         led_class_callbacks = led_class_callbacks)

def main_loop():
    global led_strip_seq
    led_strip_seq.check_event()


# main program start
init_setup()
while True:
    main_loop()
    
