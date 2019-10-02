import contextlib
with contextlib.redirect_stdout(None):
    from pygame import midi
from ipywidgets import Text
from threading import Thread
import numpy as np
import time

midi.init()

def find_device_id(device_name):
    for i in range(255):
        info = midi.get_device_info(i)
        if info[1].decode() == device_name and info[2] == 1:
            return i
        
class Knob:
    ''' Handles MIDI events for a passed parametric.Parameter instance. Each directional MIDI event is mapped
        to a step with size given by the bounds and the passed resolution. Other MIDI events can be used to toggle
        the lock state of the channel, which will force incoming directional events to be ignored.
    '''
    def __init__(self, parameter, resolution=1024):
        self.parameter = parameter
        self.resolution = resolution
        self.output = None
        self.locked = False
        
    def handle(self, direction):
        if self.locked:
            return
        x = self.parameter
        step = (x.bounds[1] - x.bounds[0])/self.resolution
        target = np.clip(x()+direction*step, *x.bounds)
        x(target)
        
        if self.output is not None:
            self.output.value = str(x)
            
    def toggle_lock(self):
        self.locked = not self.locked
        
class MIDIStream:
    ''' Opens a MIDI stream with the specified device. The passed device_name should match one of the entries given by
        pygame.midi.get_device_info(i) while iterating through integers i.
    '''
    def __init__(self, device_name, delay=0, buffer_size=1024):
        self.delay = delay
        self.buffer_size = buffer_size
        devid = find_device_id(device_name)
        self.stream = midi.Input(devid)
        self.knobs = {}
        Thread(target=self.start).start()
        
    def __del__(self):
        self.stop()
        
    def assign(self, channel, parameter, output=False):
        self.knobs[channel] = Knob(parameter)
        if output:
            text = Text()
            display(text)
            self.knobs[channel].output = text
        
    def start(self):
        self.running = True
        while self.running:
            events = self.stream.read(self.buffer_size)
            for event in events:
                ch = event[0][1]
                direction = None
                val = event[0][2]
                if val == 65:
                    direction = 1
                elif val == 63:
                    direction = -1
                    
                if ch in self.knobs:
                    if direction is not None:
                        self.knobs[ch].handle(direction)
                    elif val == 127:
                        self.knobs[ch].toggle_lock()
                        
            time.sleep(self.delay)
                        
    def stop(self):
        self.running = False