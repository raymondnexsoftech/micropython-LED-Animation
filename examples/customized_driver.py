# LED Strip
from machine import Pin
from neopixel import NeoPixel
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

# functions
def led_class_create(led_class, orig_callback, pin_number, led_count):
    # callback to create driver
    # return the created driver
    led_strip_pin = Pin(pin_number, Pin.OUT)
    return led_class(led_strip_pin, led_count)

def led_class_len(led_driver, orig_callback):
    # callback to get size of LED
    # return the length of the LED strip
    return len(led_driver)

def led_class_set_item(led_driver, orig_callback, i, value):
    # callback to set specific LED value to buffer
    # no return needed
    led_driver[i] = value

def led_class_get_item(led_driver, orig_callback, i):
    # callback to get specific LED from buffer
    # return the value of the specific LED
    return led_driver[i]

def led_class_fill(led_driver, orig_callback, value):
    # callback to fill all LEDs' buffer with same value
    # no return needed
    led_driver.fill(value)

def led_class_write(led_driver, orig_callback):
    # callback to write the buffer value to LEDs
    # no return needed
    led_driver.write()

def init_setup():
    global led_strip_seq
    # callback dictionary
    led_class_callbacks = {
        "create": led_class_create,
        "len": led_class_len,
        "set_item": led_class_set_item,
        "get_item": led_class_get_item,
        "fill": led_class_fill,
        "write": led_class_write,
    }
    led_strip_seq = LedStripAnimationSeq(LED_STRIP_PIN,
                                         LED_STRIP_COUNT,
                                         animation_seq,
                                         led_class = NeoPixel,
                                         led_class_callbacks = led_class_callbacks)

def main_loop():
    global led_strip_seq
    led_strip_seq.check_event()


# main program start
init_setup()
while True:
    main_loop()
    


