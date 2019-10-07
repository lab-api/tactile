import attr
from ipywidgets import Text
import numpy as np

@attr.s
class Knob:
    parameter = attr.ib()
    display_events = attr.ib(default=False, converter=bool)
    output = attr.ib(default=None)
    locked = attr.ib(default=False, converter=bool)

    def display(self, message):
        if self.display_events:
            if self.output is None:
                self.output = Text()
                display(self.output)
            self.output.value = str(message)

    def toggle_lock(self):
        self.locked = not self.locked

@attr.s
class AbsoluteKnob(Knob):
    ''' Represents a knob with absolute positioning, whose value 0-127 is mapped
        to the parameter bounds.
    '''
    mode = 'absolute'

    def handle(self, value):
        if self.locked:
            return
        x = self.parameter
        target = x.bounds[0] + (x.bounds[1]-x.bounds[0])*value/127
        x(target)
        self.display(x)

@attr.s
class RelativeKnob(Knob):
    ''' Handles MIDI events for a passed parametric.Parameter instance. Each directional MIDI event is mapped
        to a step with size given by the bounds and the passed resolution. Other MIDI events can be used to toggle
        the lock state of the channel, which will force incoming directional events to be ignored.
    '''
    resolution = attr.ib(default=1024, converter=float)
    mode='relative'

    def handle(self, direction):
        if self.locked:
            return
        x = self.parameter
        step = (x.bounds[1] - x.bounds[0])/self.resolution
        target = np.clip(x()+direction*step, *x.bounds)
        x(target)

        self.display(x)
