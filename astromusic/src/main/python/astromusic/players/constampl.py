import queue
import sys
import threading
import time

import numpy as np
import sounddevice as sd


class ConstAmplPlayer:
    MAX_AMPL = 2 ** 15 - 1

    def __init__(self, blocksize=2205, buffersize=20, samplerate=44100):
        self.blocksize = blocksize
        self.buffersize = buffersize
        self.samplerate = samplerate

        self.queue = queue.Queue(maxsize=buffersize)
        self.event = threading.Event()
        self.freq = 440
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

            #             w = (2 ** 15 - 1) * np.sin(2 * np.pi * old_freq * (self.offset + self.t))
            #             tswitch = np.arange(0, len(self.t) - 1)[(w[:-1] < 0) & (w[1:] >= 0)][0] + 1
            #             self.offset = w[tswitch] / (w[tswitch] - w[tswitch - 1]) * (self.t[tswitch] - self.t[tswitch - 1])
            #             w[tswitch:] = (2 ** 15 - 1) * np.sin(2 * np.pi * self.freq * (self.offset + self.t[:-tswitch]))

            # self.offset = self.t[-tswitch]
            #             w *= self.t / self.t[-1]
            #             w += (2 ** 15 - 1) * (self.t[-1]-self.t) / self.t[-1] \
            #             * np.sin(2 * np.pi * old_freq * (self.offset + self.t))
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
        i = 0
        for i in range(self.buffersize):
            self.queue.put_nowait(self.wave())

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
                        i += 1
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

    def stop(self):
        self.is_running = False
        if self.thread is not None:
            self.thread.join()
            self.thread = None
        if not self.queue.empty():
            self.clear_queue()

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
                self.fig, self.ax = self.plt.subplots()
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
                    self.freq_slider, self.freq_scala)  # , self.fig)

        def set_freq(self, e):
            self.player.set_freq(self.base_freq * self.HALFTONE ** e.new)
            self.freq_label.value = f'{self.player.freq} Hz'
            self.plot()

        def start(self, _):
            self.player.start()

        def stop(self, _):
            self.player.stop()
