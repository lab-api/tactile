# tactile
Tactile gives experimental control systems a touch of human friendliness by allowing simple interfacing with MIDI controllers through the [Parametric](https://github.com/lab-api/parametric) device control framework. As a simple example, let's open a MIDI input stream to a 16-knob controller and bind two parameters to channels 0 and 1:

```python
from parametric import Parameter
from tactile import MIDIStream

stream = MIDIStream('Midi Fighter Twister')

x = Parameter('x', 0, bounds = (-1, 1))
y = Parameter('y', 0, bounds = (-1, 1))

stream.assign(0, x, output=True)
stream.assign(1, y, output=True)
```
