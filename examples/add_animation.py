# LED Strip
from led_animation_seq import LedStripAnimationSeq, add_led_strip_animation
LED_STRIP_PIN = 12
LED_STRIP_COUNT = 20

# LED Strip Animation
led_strip_seq = None
animation_seq = [
    ['special_blink_all', 5000],
    [None, 5000, {"active_count": 1, "colors": (100, 100, 100)}],
]

# functions
def special_blink_all_setup(led_driver, attributes):
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
    # the "__next_delay__" here is to indicate the time for next animation
    # skip this to use the "speed" value in attributes,
    #   or default value if no "speed" in attributes
    state["__next_delay__"] = 100 if cur_led_state else 500
    return state

def special_blink_all_next_step(led_driver, state):
    cur_led_state = state.get("cur_led_state", True)
    colors = state.get("colors", (200, 200, 200))
    # start next step
    state["cur_led_state"] = not cur_led_state
    led_driver.fill(colors if cur_led_state else (0, 0, 0))
    led_driver.write()
    # the "__next_delay__" here is to indicate the time for next animation
    # originally there is exist "__next_delay__" in state
    # remain the value or set as None will use the last "__next_delay__" value
    state["__next_delay__"] = 100 if cur_led_state else 500
    return state

# return of "add_led_strip_animation" indicate whether the animation is added successfully
# if return False, that means cannot add animation.
#   One of the reason is the name of the animation already existed
#   To overwrite, add "confirm_overwrite = True" when calling add_led_strip_animation
is_add_animation = add_led_strip_animation("special_blink_all", {
        "setup": special_blink_all_setup,
        "next_step": special_blink_all_next_step
    })

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
    
