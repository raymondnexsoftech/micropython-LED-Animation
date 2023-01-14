MicroPython LED Animation
============================

MicroPython LED strip animation library
- Default using "NeoPixel" as LED driver, but you can use you favourite driver with some callback to work
- Able to add your customized animation
- Can trigger animation events (animation next step, next animation) manually or using system loop


Installation
------------

Copy `led_animation_seq.py` file to your board.

Usage
-----

**Basic usage:**

```python
from led_animation_seq import LedStripAnimationSeq
led_strip_seq = None
LED_STRIP_PIN = 12
LED_STRIP_COUNT = 20
animation_seq = [
    ['move_up_with_tail', 5000, {"speed": 50, "active_count": 1, "colors": (100, 100, 100)}],
    ['none', 5000],
]
led_strip_seq = LedStripAnimationSeq(LED_STRIP_PIN,
                                     LED_STRIP_COUNT,
                                     animation_seq)

...

# In main program loop:
while(True):
    led_strip_seq.check_event()
```

**Basic usage with sequence callbacks:**

```python
from led_animation_seq import LedStripAnimationSeq
led_strip_seq = None
LED_STRIP_PIN = 12
LED_STRIP_COUNT = 20
animation_seq = [
    ['blink_all', 5000],
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

led_strip_seq = LedStripAnimationSeq(LED_STRIP_PIN,
                                     LED_STRIP_COUNT,
                                     animation_seq,
                                     seq_callbacks = seq_callbacks)

...

# In main program loop:
while(True):
    led_strip_seq.check_event()
```

**Use customized driver:**

```python
from neopixel import NeoPixel
from led_animation_seq import LedStripAnimationSeq
led_strip_seq = None
LED_STRIP_PIN = 12
LED_STRIP_COUNT = 20
animation_seq = [
    ['move_up_with_tail', 5000, 50, {"active_count": 1, "colors": (100, 100, 100)}],
    ['none', 5000],
]

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


...

# In main program loop:
while(True):
    led_strip_seq.check_event()
```

**Advance example - customize setting using default driver:**  

You can use default LED driver with customized callback  
The example here is to use customized create function to apply different timing on driver, and print notice when calling fill function  
\*Note: please call the "orig_callback" if you just want to add addition code instead of rewrite the callback  
The paramaters of the callback is the same as the input of customized callback without the first two arguments  

```python
from machine import Pin

...

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

led_class_callbacks = {
    "create": led_class_create,
    "fill": led_class_fill,
}

led_strip_seq = LedStripAnimationSeq(LED_STRIP_PIN,
                                     LED_STRIP_COUNT,
                                     animation_seq,
                                     led_class_callbacks = led_class_callbacks)

...

# In main program loop:
while(True):
    led_strip_seq.check_event()
```

**Add customized animation:**

```python
from led_animation_seq import add_led_strip_animation

...

def blink_all_setup(led_driver, attributes):
    if (attributes is None):
        attributes = {}
    start_from_off = attributes.get("start_from_off", True)
    colors = attributes.get("colors", (200, 200, 200))
    # start setup
    cur_led_state = not start_from_off
    led_driver.fill(colors if cur_led_state else (0, 0, 0))
    led_driver.write()
    state = {
        "cur_led_state" : cur_led_state,
        "colors": colors
        }
    return state

def blink_all_next_step(led_driver, state):
    cur_led_state = state.get("cur_led_state", True)
    colors = state.get("colors", (200, 200, 200))
    # start next step
    state["cur_led_state"] = not cur_led_state
    led_driver.fill(colors if cur_led_state else (0, 0, 0))
    led_driver.write()
    return state

add_led_strip_animation("blink_all", {
        "setup": blink_all_setup,
        "next_step": blink_all_next_step
    })
```

**Manual trigger events:**

```python
import time
from led_animation_seq import LedStripAnimationSeq
led_strip_seq = None
LED_STRIP_PIN = 12
LED_STRIP_COUNT = 20
animation_seq = [
    ['move_up_with_tail', 5000, 50, {"active_count": 1, "colors": (100, 100, 100)}],
    ['none', 5000],
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

```

Examples
--------

`examples/basic_usage.py` - Simple demo  
`examples/basic_usage_with_callback.py` - Simple demo with callbacks  
`examples/customized_driver.py` - Demo with customized driver  
`examples/default_driver_customize.py` - customize callback of the default driver  
`examples/add_animation.py` - Demo to add new animation  
`examples/manual_trigger.py` - Demo for manual trigger event  

Function Description
--------------------

TODO:



Further Development
-------------------

Due to the `LedDriverWrapper` class, I think more LED modules like 8x8 Matrix can also implement in here.  
However it is not likely for me to do such implementation.  
If someone interested to do, feel free to fork a new repo and continue to develop.  
Please also let me know if you do this so that I can redirect the user to your new repo ;-).  


More info & Help
----------------

You can check more about the MicroPython project here: http://micropython.org
