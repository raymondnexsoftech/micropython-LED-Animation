from machine import Pin
from time import ticks_ms, ticks_diff
import math

# The preset animation are defined at the bottom of this files
led_animation_mapping_callbacks = {}

def add_led_strip_animation(animation_name, callbacks, confirm_overwrite = False):
    global led_animation_mapping_callbacks
    if (animation_name is None):
        # don't add any animation if no name provided
        return False
    if (led_animation_mapping_callbacks.get(animation_name, None) is not None):
        if (confirm_overwrite == false):
            # since the animation exist, if not confirm overwrite, stop saving to protect the old animation
            return False
    led_animation_mapping_callbacks[animation_name] = callbacks
    return True

# wrap custom LED driver to NeoPixel like methods
# will assume the same way to call NeoPixel for missing callbacks
class LedDriverWrapper():
    def __init__(self, led_class, pin_number, led_count, callbacks = {}):
        self.callbacks = callbacks
        if (led_class is None):
            # if no led_class provided, default will use NeoPixel and all use default callbacks
            from neopixel import NeoPixel
            led_class = NeoPixel
        if callbacks.get("create", None) is not None:
            self.callbacks = callbacks
            self.led_driver = callbacks["create"](led_class, self.orig_create_callback, pin_number, led_count)
        else:
            self.led_driver = self.orig_create_callback(led_class, pin_number, led_count)

    def __len__(self):
        if (self.callbacks.get("len", None) is not None):
            return self.callbacks["len"](self.led_driver, self.orig_len_callback)
        else:
            return self.orig_len_callback()

    def __setitem__(self, i, v):
        if (self.callbacks.get("set_item", None) is not None):
            self.callbacks["set_item"](self.led_driver, self.orig_setitem_callback, i, v)
        else:
            self.orig_setitem_callback(i, v)

    def __getitem__(self, i):
        if (self.callbacks.get("get_item", None) is not None):
            return self.callbacks["get_item"](self.led_driver, self.orig_getitem_callback, i)
        else:
            return self.orig_getitem_callback(i)

    def fill(self, v):
        if (self.callbacks.get("fill", None) is not None):
            self.callbacks["fill"](self.led_driver, self.orig_fill_callback, v)
        else:
            self.orig_fill_callback(v)

    def write(self):
        if (self.callbacks.get("write", None) is not None):
            self.callbacks["write"](self.led_driver, self.orig_write_callback)
        else:
            self.orig_write_callback()
            
    
    # function to remap the correct index for rotating LED strip
    def remap_led_index(self, index):
        while (index < 0):
            index += len(self.led_driver)
        while (index >= len(self.led_driver)):
            index -= len(self.led_driver)
        return index
    
    # original callback for LED driver
    def orig_create_callback(self, led_class, pin_number, led_count):
        led_strip_pin = Pin(pin_number, Pin.OUT)
        return led_class(led_strip_pin, led_count)

    def orig_len_callback(self):
        return len(self.led_driver)

    def orig_setitem_callback(self, i, v):
        self.led_driver[i] = v

    def orig_getitem_callback(self, i):
        return self.led_driver[i]

    def orig_fill_callback(self, v):
        self.led_driver.fill(v)

    def orig_write_callback(self):
        self.led_driver.write()

# manage animation sequence
class LedStripAnimationSeq():
    def __init__(self, pin_number, led_count, animation_seq, led_class = None, led_class_callbacks = {}, manual_trigger_event = False, seq_callbacks = {}):
        self.led_driver = LedDriverWrapper(led_class, pin_number, led_count, led_class_callbacks)            
        self.led_count = led_count
        self.animation_seq = animation_seq
        self.manual_trigger_event = manual_trigger_event
        self.seq_callbacks = seq_callbacks
        self.animation_seq_step = 0
        self.animation = None
        self.next_action_time_ms = None
        self.start_animation()
    
    # start next animation
    def next_animation(self):
        self.animation_seq_step += 1
        self.start_animation()

    def start_animation(self):
        self.animation_seq_step = self.remap_animation_step(self.animation_seq_step)
        cur_step = self.animation_seq[self.animation_seq_step]
        cur_step_len = len(cur_step)
        animation_name = cur_step[0]
        animation_duration = cur_step[1]
        animation_attribute = cur_step[2] if cur_step_len > 2 else None
        self.animation = LedStripAnimation(self.led_driver,
                                           animation_name,
                                           animation_attribute)
        self.next_action_time_ms = None if animation_duration is None or animation_duration == 0 else ticks_ms() + animation_duration
    
    # function to check if any event triggered by time (animation change seq, animation next step)
    def check_event(self):
        if (not self.manual_trigger_event):
            if ((self.next_action_time_ms is not None) and
                (ticks_diff(ticks_ms(), self.next_action_time_ms) > 0)):
                # check which callback should run
                self.animation_seq_step += 1
                if (self.animation_seq_step >= len(self.animation_seq)):
                    # run "seq_end" callback since it is already over the list
                    callback = self.seq_callbacks.get("seq_end", None)
                    if (callback is not None):
                        animation_seq_step = callback()
                        if (animation_seq_step is not None):
                            self.animation_seq_step = max(min(animation_seq_step, len(self.animation_seq)), 0)
                else:
                    # run "change_animation" callback
                    callback = self.seq_callbacks.get("change_animation", None)
                    if (callback is not None):
                        animation_seq_step = callback(self.animation_seq_step)
                        if (animation_seq_step is not None):
                            self.animation_seq_step = max(min(animation_seq_step, len(self.animation_seq)), 0)
                self.start_animation()
            else:
                self.animation.check_event()
    
    # function to trigger animation event (use at manual mode)
    def trigger_animation_event(self):
         self.animation.trigger_event()
    
    # function to remap the correct animation step for rotating sequence
    def remap_animation_step(self, step):
        while (step < 0):
            step += len(self.animation_seq)
        while (step >= len(self.animation_seq)):
            step -= len(self.animation_seq)
        return step            
        

class LedStripAnimation():
    def __init__(self, led_driver, animation_type, attributes):
        global led_animation_mapping_callbacks
        self.led_driver = led_driver
        self.animation_type = animation_type
        self.attributes = attributes if attributes is not None else {}
        self.led_animation_callbacks = led_animation_mapping_callbacks.get(self.animation_type, None)
        self.state = {}
        
        # Setup animation
        led_animation_setup = None
        if (self.led_animation_callbacks is not None):
            led_animation_setup = self.led_animation_callbacks.get("setup", None)
        if (led_animation_setup is not None):
            self.state = led_animation_setup(self.led_driver, self.attributes)
            if (self.state is None):
                self.state = {}
        else:     # No setup match, assume all LEDs are off
            self.led_animation_callbacks = None
            for i in range(len(self.led_driver)):
                self.led_driver[i] = (0, 0, 0)

        self.next_delay = self.state.get("__next_delay__", None)
        if (self.next_delay is None):
            self.next_delay = self.attributes.get("speed", 500) if (isinstance(self.attributes, dict)) else 500
        self.state["__next_delay__"] = self.next_delay
        self.next_action_time_ms = None if self.next_delay is None or self.next_delay == 0 else ticks_ms() + self.next_delay

        # Set LED lights
        self.led_driver.write()

    # function to check if any event triggered by time
    def check_event(self):
        if (self.animation_type is not None):
            if (self.next_action_time_ms is not None):
                if (ticks_diff(ticks_ms(), self.next_action_time_ms) > 0):
                    self.trigger_event()
    
    # trigger event (animation next step)
    def trigger_event(self):
        led_animation_next_step_callback = None
        if (self.led_animation_callbacks is not None):
            led_animation_next_step_callback = self.led_animation_callbacks.get("next_step", None)
        if (led_animation_next_step_callback is not None):
            self.state = led_animation_next_step_callback(self.led_driver, self.state)
            if (self.state is None):
                self.state = {}
            new_next_delay = self.state.get("__next_delay__", None)
            if (new_next_delay is not None):
                self.next_delay = new_next_delay
        self.next_action_time_ms = None if self.next_delay is None or self.next_delay == 0 else ticks_ms() + self.next_delay



#####################################
# Preset animation functions
#####################################
def move_left_with_tail_setup(led_driver, attributes):
    if (attributes is None):
        attributes = {}
    active_count = attributes.get("active_count", 1)
    max_tail_count = attributes.get("max_tail_count", 10)
    if (max_tail_count <= 0):
        max_tail_count = 1
    colors = attributes.get("colors", (200, 200, 200))
    # start setup
    led_driver.fill((0, 0, 0))
    active_count_distance = len(led_driver) / active_count
    next_led_position_double = 0
    next_led_position = 0
    for i in range(active_count):
        led_position_double = next_led_position_double
        led_position = next_led_position
        next_led_position_double = led_position_double + active_count_distance
        next_led_position = math.floor(next_led_position_double)
        tail_count = min(next_led_position - led_position, max_tail_count)
        for j in range(tail_count):
            led_driver[led_position] = (math.floor((tail_count - j) / tail_count * colors[0]),
                                            math.floor((tail_count - j) / tail_count * colors[1]),
                                            math.floor((tail_count - j) / tail_count * colors[2]))
            led_position = led_driver.remap_led_index(led_position + 1)
        led_driver.write()

def move_left_with_tail_next_step(led_driver, state):
    # start next step
    pos_0_value = led_driver[0]
    for i in range(len(led_driver)):
        led_driver[i] = led_driver[led_driver.remap_led_index(i + 1)]
    led_driver[len(led_driver) - 1] = pos_0_value
    led_driver.write()

add_led_strip_animation("move_left_with_tail", {
        "setup": move_left_with_tail_setup,
        "next_step": move_left_with_tail_next_step
    })


def move_right_with_tail_setup(led_driver, attributes):
    if (attributes is None):
        attributes = {}
    active_count = attributes.get("active_count", 1)
    max_tail_count = attributes.get("max_tail_count", 10)
    if (max_tail_count <= 0):
        max_tail_count = 1
    colors = attributes.get("colors", (200, 200, 200))
    # start setup
    led_driver.fill((0, 0, 0))
    active_count_distance = len(led_driver) / active_count
    next_led_position_double = len(led_driver)
    next_led_position = len(led_driver)
    for i in range(active_count):
        led_position_double = next_led_position_double
        led_position = next_led_position
        next_led_position_double = led_position_double - active_count_distance
        next_led_position = math.floor(next_led_position_double)
        tail_count = min(led_position - next_led_position, max_tail_count)
        for j in range(tail_count):
            led_driver[led_position - 1] = (math.floor((tail_count - j) / tail_count * colors[0]),
                                            math.floor((tail_count - j) / tail_count * colors[1]),
                                            math.floor((tail_count - j) / tail_count * colors[2]))
            led_position = led_driver.remap_led_index(led_position - 1)
        led_driver.write()

def move_right_with_tail_next_step(led_driver, state):
    # start next step
    last_pos_value = led_driver[len(led_driver) - 1]
    for i in reversed(range(len(led_driver))):
        led_driver[led_driver.remap_led_index(i + 1)] = led_driver[i]
    led_driver[0] = last_pos_value
    led_driver.write()

add_led_strip_animation("move_right_with_tail", {
        "setup": move_right_with_tail_setup,
        "next_step": move_right_with_tail_next_step
    })


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

