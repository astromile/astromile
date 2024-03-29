import queue
import sys
import threading
import time

import ipywidgets as ui
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd

from astromusic.players.player import SinWave, Player
from astromusic.util import deprecated


class VariableWave(SinWave):
    class Param:
        Frequency = 'freq'
        Amplitude = 'amplitude'
        Phase = 'phase'

    class Message:
        def __init__(self, param, value):
            self.param = param
            self.value = value

    def __init__(self, amplitude=1, freq=440, phase=0):
        super().__init__(amplitude, freq, phase)
        self.messages = queue.Queue()

    def modify(self, param, value):
        self.messages.put_nowait(self.Message(param, value))

    def set_freq(self, freq):
        self.modify(self.Param.Frequency, freq)

    def set_amplitude(self, amplitude):
        self.modify(self.Param.Amplitude, amplitude)

    def set_phase(self, phase):
        self.modify(self.Param.Phase, phase)

    def wave(self, t):
        freq = self.freq
        amplitude = self.amplitude
        phase = self.phase
        while not self.messages.empty():
            message = self.messages.get_nowait()
            if message.param == self.Param.Frequency:
                freq = message.value
            elif message.param == self.Param.Amplitude:
                amplitude = message.value
            elif message.param == self.Param.Phase:
                phase = message.value
            else:
                pass  # skip unknown message

        if self.phase != phase:
            self.phase = phase
            self.freq = freq

        elif self.freq != freq:
            """ magic to smoothly jump from one wave line to another one """
            dt = t[1] - t[0]
            prv, nxt = super().wave(np.array([t[0] - dt, t[0]]))
            x = np.arcsin(
                nxt / self.amplitude if self.amplitude != 0.0 else 0.0)  # point of intercept: A * sin(x) == Signal(old freq, t[0])
            if prv > nxt:
                x = np.pi - x
            # phase of intercept for new freq: A * sin(x) = A * sin(2 * pi * freq * t0 + phase)
            self.phase = (x - 2 * np.pi * freq * t[0])  # % (2 * np.pi)
            self.freq = freq

        if self.amplitude != amplitude:
            if amplitude == 0.0:
                smoother = (t[-1] - t) / (t[-1] - t[0])
                wave = super().wave(t) * smoother
                self.amplitude = amplitude
                return wave
            else:
                smoother = (self.amplitude / amplitude * (t[-1] - t) + t - t[0]) / (t[-1] - t[0])
                self.amplitude = amplitude
                return super().wave(t) * smoother
        else:
            return super().wave(t)


@deprecated("Use combination Player and VaryFreqWave")
class ConstAmplPlayer:
    MAX_AMPL = 2 ** 15 - 1

    def __init__(self, blocksize=2205, buffersize=20, samplerate=44100, freq=440):
        self.blocksize = blocksize
        self.buffersize = buffersize
        self.samplerate = samplerate

        self.queue = queue.Queue(maxsize=buffersize)
        self.event = threading.Event()
        self.freq = freq
        self.is_running = False
        self.offset = 0
        self.dt = 1 / self.samplerate
        self.t = np.arange(0, self.blocksize / self.samplerate, self.dt)
        self.thread = None
        self.lock = threading.Lock()

    def callback(self, outdata, frames, _, status):
        # print(self.freq)
        if not self.is_running:
            # print('stopping...', file=sys.stderr)
            raise sd.CallbackAbort
        assert frames == self.blocksize
        if status.output_underflow:
            print('Output underflow: increase blocksize?', file=sys.stderr)
            raise sd.CallbackAbort
        assert not status
        try:
            data = self.queue.get_nowait()
            if len(data) < len(outdata):
                outdata[:len(data)] = data
                outdata[len(data):] = b'\x00' * (len(outdata) - len(data))
                raise sd.CallbackStop
            else:
                outdata[:] = data
        except queue.Empty:
            print('Buffer is empty, using silence wave instead: increase buffersize?', file=sys.stderr)
            # raise sd.CallbackAbort
            outdata[:] = b'\x00' * len(outdata)

    def wave(self, old_freq=None):
        with self.lock:
            w = np.sin(2 * np.pi * self.freq * (self.offset + self.t))
            if old_freq is not None:
                # magic to smoothly jump from one wave line to another one
                prv, nxt = np.sin(2 * np.pi * old_freq * (self.offset + np.array([-self.dt, 0])))
                offset = np.arcsin(nxt)
                if prv > nxt:
                    offset = np.pi - offset
                w = np.sin(offset + 2 * np.pi * self.freq * self.t)
                self.offset = offset / (2 * np.pi * self.freq) + self.blocksize / self.samplerate
            else:
                self.offset += self.blocksize / self.samplerate

            w *= self.MAX_AMPL
            data = np.empty((self.blocksize, 2), dtype=np.int16)
            data[:, 0] = w
            data[:, 1] = w
            return data.tobytes()

    def start(self):
        if self.is_running or self.thread is not None or not self.queue.empty():
            self.stop()

        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def run(self):
        self.offset = 0.0
        [self.queue.put_nowait(self.wave()) for _ in range(self.buffersize)]

        with sd.RawOutputStream(samplerate=self.samplerate,
                                blocksize=self.blocksize,
                                channels=2, dtype='int16',
                                callback=self.callback,
                                finished_callback=self.event.set):
            timeout = self.blocksize * self.buffersize / self.samplerate
            self.is_running = True
            freq = self.freq
            while self.is_running:
                try:
                    if freq != self.freq:
                        if self.is_running:
                            self.queue.put(self.wave(freq))
                        freq = self.freq
                    else:
                        if self.is_running:
                            self.queue.put(self.wave(), timeout=timeout)
                except queue.Full:
                    if self.is_running:
                        print('queue is full')
                        time.sleep(0.1)
            self.event.wait()

    @staticmethod
    def play(wave):
        sd.play(wave)

    def set_freq(self, freq):
        with self.lock:
            self.freq = freq

    def clear_queue(self):
        data = None
        while not self.queue.empty():
            data = self.queue.get_nowait()
        return data

    def stop(self, blocking=True):
        self.is_running = False
        if blocking and self.thread is not None:
            self.thread.join()
            self.thread = None
        if not self.queue.empty():
            self.clear_queue()

    @deprecated('Use players.constampl.UI class instead.')
    class UI:
        import ipywidgets as ui
        import matplotlib.pyplot as plt
        HALFTONE = 2 ** (1 / 12)
        TONES = 36
        TONE = ['A', 'A#', 'H', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']

        def __init__(self, blocksize=4410, buffersize=2, samplerate=44100, freq=440, fig=None, ax=None):
            self.player = ConstAmplPlayer(blocksize=blocksize, buffersize=buffersize, samplerate=samplerate)
            self.base_freq = freq / 2
            self.player.freq = self.freq = freq

            self.freq_label = self.ui.Label(value=f'{self.freq} Hz')

            self.start_button = self.ui.Button(description='Start')
            self.start_button.on_click(self.start)

            self.stop_button = self.ui.Button(description='Stop')
            self.stop_button.on_click(self.stop)

            self.freq_slider = self.ui.IntSlider(value=12, min=0, max=self.TONES, step=1,
                                                 layout=self.ui.Layout(width='100%'))
            self.freq_slider.observe(self.set_freq, names='value')

            layout = self.ui.Layout(width='2.12%')
            self.freq_scala = self.ui.HBox([self.ui.Label()]
                                           + [self.ui.Label(value=self.TONE[i % 12], layout=layout)
                                              for i in range(self.TONES + 1)])
            if fig is None or ax is None:
                self.plt.ioff()
                self.fig, self.ax = self.plt.subplots()
                self.plt.ion()
            else:
                self.fig, self.ax = fig, ax
            self.plot(show=False)

        def plot(self, show=True):
            self.ax.clear()
            self.ax.plot(self.player.t, np.sin(2 * np.pi * self.player.freq * self.player.t))
            self.ax.set_xlim(0, 1 / self.base_freq)
            self.ax.grid()
            # if show:
            #    self.fig.show()

        # noinspection PyTypeChecker
        def show(self):
            from IPython.display import display
            display(self.ui.HBox([self.start_button, self.stop_button, self.freq_label]),
                    self.freq_slider, self.freq_scala, self.fig)

        def set_freq(self, e):
            self.player.set_freq(self.base_freq * self.HALFTONE ** e.new)
            self.freq_label.value = f'{self.player.freq} Hz'
            self.plot()

        def start(self, _):
            self.player.start()

        def stop(self, _):
            self.player.stop()


class UI(ui.VBox):
    HALFTONE = 2 ** (1 / 12)
    TONES = 36
    TONE = ['A', 'A#', 'H', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']

    def __init__(self, blocksize=4410, buffersize=2, samplerate=44100, freq=440):
        self.wave = VariableWave(freq=freq)
        self.display_wave = VariableWave(freq=freq)
        self.player = Player(wave=self.wave, blocksize=blocksize, buffersize=buffersize, samplerate=samplerate)
        self.base_freq = freq / 2

        self.freq_label = ui.Label(value=f'{self.wave.freq} Hz')

        self.button = ui.Button(icon='fa-play')
        self.button.on_click(self.switch)

        self.freq_slider = ui.IntSlider(value=12, min=0, max=self.TONES, step=1, readout=False,
                                        layout=ui.Layout(width='100%', margin='0', padding='10px'))
        self.freq_slider.observe(self.set_freq, names='value')

        layout = ui.Layout(width='2.27%', display='flex', justify_content='center')
        self.freq_scala = ui.HBox([ui.Label()]
                                  + [ui.Label(value=self.TONE[i % 12], layout=layout)
                                     for i in range(self.TONES + 1)])
        plt.ioff()
        self.fig, self.ax = plt.subplots()
        # plt.ion()  # interactive mode should stay off, otherwise dynamic plot will exhibit graphical artefacts
        self.offset = 0

        self.queue = queue.Queue()
        self.queue.put_nowait('stop')

        super().__init__([
            ui.HBox([self.button, self.freq_label]),
            self.freq_slider,
            self.freq_scala,
            self.fig.canvas
        ])

        self.plot()

    def plot(self):
        self.ax.clear()
        self.display_wave.freq = self.freq()
        t = self.offset + np.linspace(0, 1 / self.base_freq, 101)
        self.ax.plot(t, self.display_wave.wave(t))
        self.ax.set_xlim(t[0], t[-1])
        self.ax.grid()
        self.fig.canvas.draw()

    def set_freq(self, _):
        freq = self.freq()
        self.wave.set_freq(freq)
        self.freq_label.value = f'{round(100 * freq) / 100} Hz'
        if not self.queue.empty():
            self.plot()

    def freq(self):
        # noinspection PyTypeChecker
        return self.base_freq * self.HALFTONE ** self.freq_slider.value

    def switch(self, _):
        if self.queue.empty():
            self.queue.put_nowait('stop')
            self.player.stop()
            self.button.icon = 'fa-play'
        else:
            while not self.queue.empty():
                self.queue.get_nowait()
            threading.Thread(target=self.run).start()
            self.player.start()
            self.button.icon = 'fa-pause'

    def run(self):
        while self.queue.empty():
            self.plot()
            time.sleep(0.01)
            self.offset += 1 / self.base_freq / 20


def _test_vary_freq():
    ht = 2 ** (1 / 12)
    wave = VariableWave(freq=440 * ht)
    player = Player(wave)
    player.start()
    for _ in range(10):
        # time.sleep(np.random.rand())
        old_freq = wave.freq
        new_freq = 440 * ht ** np.random.randint(1, 12)
        wave.set_freq(new_freq)
        print(old_freq, '->', new_freq)
    for _ in range(10):
        time.sleep(np.random.rand())
        old_freq = wave.freq
        new_freq = 440 * ht ** np.random.randint(1, 12)
        wave.set_freq(new_freq)
        print(old_freq, '->', new_freq)

    time.sleep(1)
    player.stop()


if __name__ == '__main__':
    _test_vary_freq()
