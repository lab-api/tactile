import contextlib
with contextlib.redirect_stdout(None):
    from pygame import midi
    midi.init()
from ipywidgets import Text
from threading import Thread
import time
import attr
from abc import abstractmethod
from tactile.knobs import RelativeKnob, AbsoluteKnob

def find_device_id(device_name):
    for i in range(255):
        info = midi.get_device_info(i)
        if info[1].decode() == device_name and info[2] == 1:
            return i

class MIDIEvent:
    def __init__(self, event):
        self.timestamp = event[1]
        self.channel = event[0][1]
        self.value = event[0][2]

    def __repr__(self):
        return f'MIDI event: value {self.value} on channel {self.channel}'

@attr.s
class MIDIStream:
    ''' Opens a MIDI stream with the specified device. The passed device_name should match one of the entries given by
        pygame.midi.get_device_info(i) while iterating through integers i.
    '''
    device_name = attr.ib(converter=str)
    delay = attr.ib(default=0, converter=float)
    buffer_size = attr.ib(default=1024, converter=int)
    display_events = attr.ib(default=False, converter=bool)
    knobs = attr.ib(factory=dict)

    @abstractmethod
    def handle(self, ch, val):
        pass

    def start(self):
        if self.display_events:
            self.output = Text()
            display(self.output)

        devid = find_device_id(self.device_name)
        self.stream = midi.Input(devid)
        Thread(target=self.run).start()
        return self

    def __del__(self):
        self.stop()

    def run(self):
        self.running = True
        while self.running:
            events = self.stream.read(self.buffer_size)
            for event in events:
                inst = MIDIEvent(event)
                if self.display_events:
                    self.output.value = str(inst)
                self.handle(inst)
            time.sleep(self.delay)

    def stop(self):
        self.running = False
        time.sleep(self.delay + 0.1)
        self.stream.close()

@attr.s
class AbsoluteStream(MIDIStream):
    def assign(self, channel, parameter):
        self.knobs[channel] = AbsoluteKnob(parameter, display_events = self.display_events)

    def handle(self, event):
        if event.channel in self.knobs:
            self.knobs[event.channel].handle(event.value)

@attr.s
class RelativeStream(MIDIStream):
    plus_value = attr.ib(default=None)
    minus_value = attr.ib(default=None)
    resolution = attr.ib(default=1024, converter=float)

    def assign(self, channel, parameter):
        self.knobs[channel] = RelativeKnob(parameter, resolution = self.resolution, display_events = self.display_events)

    def handle(self, event):
        if event.channel in self.knobs:
            direction = {self.plus_value: 1, self.minus_value: 0}[event.value]
            self.knobs[event.channel].handle(direction)
