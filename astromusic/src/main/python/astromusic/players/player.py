import queue
import sys
import threading
import time

import numpy as np
import sounddevice as sd


class Wave:
    DTYPE = np.int16
    MAX_AMPL = 2 ** 15 - 1
    TWOPI = 2 * np.pi

    # noinspection PyMethodMayBeStatic
    def wave(self, t):
        return np.zeros(np.shape(t))


class SinWave(Wave):
    def __init__(self, amplitude=1, freq=440, phase=0):
        """
        Classical Sin-Wave
        :param amplitude: signal amplitude, number from [0,1]
        :param freq: signal frequency
        :param phase: signal phase
        """
        assert 0 <= amplitude <= 1
        self.amplitude = amplitude
        self.freq = freq
        self.phase = phase

    def wave(self, t):
        return self.amplitude * np.sin(self.TWOPI * self.freq * t + self.phase)


class Player:
    CHANNELS = 2

    def __init__(self, wave, right_wave=None,
                 blocksize=2205, buffersize=20, samplerate=44100):
        self.wave = wave
        self.right_wave = right_wave
        self.blocksize = blocksize
        self.buffersize = buffersize
        self.samplerate = samplerate
        self.dt = 1 / samplerate
        self.tblock = blocksize / samplerate
        self.t = np.arange(0, self.tblock, self.dt)
        self.tcum = 0

        self.queue = queue.Queue(maxsize=buffersize)
        self.event = threading.Event()
        self.is_running = False
        self.thread = None

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

    def get_wave(self):
        t = self.tcum + self.t
        self.tcum += self.tblock
        data = np.empty([self.blocksize, self.CHANNELS], dtype=Wave.DTYPE)
        left_wave = Wave.MAX_AMPL * self.wave.wave(t)
        if self.CHANNELS == 1 or self.right_wave is None:
            for channel in range(self.CHANNELS):
                data[:, channel] = left_wave
        else:
            right_wave = Wave.MAX_AMPL * self.right_wave.wave(t)
            data[:, 0] = left_wave
            for channel in range(1, self.CHANNELS):
                data[:, channel] = right_wave

        return data.tobytes()

    def start(self):
        if self.is_running or self.thread is not None or not self.queue.empty():
            self.stop()

        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def run(self):
        [self.queue.put_nowait(self.get_wave()) for _ in range(self.buffersize)]

        with sd.RawOutputStream(samplerate=self.samplerate,
                                blocksize=self.blocksize,
                                channels=2, dtype='int16',
                                callback=self.callback,
                                finished_callback=self.event.set):
            timeout = self.blocksize * self.buffersize / self.samplerate
            self.is_running = True
            while self.is_running:
                try:
                    if self.is_running:
                        self.queue.put(self.get_wave(), timeout=timeout)
                except queue.Full:
                    if self.is_running:
                        print('queue is full')
                        time.sleep(0.1)

            self.event.wait()

    @staticmethod
    def play(wave):
        if isinstance(wave, list) or isinstance(wave, tuple):
            wave = np.array(wave)
        if isinstance(wave, bytes):
            wave = np.frombuffer(wave, dtype=np.int16)
        if isinstance(wave, np.ndarray):
            sd.play(wave)
        else:
            raise TypeError(f'Unsupported type of wave: {type(wave)}')

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


if __name__ == '__main__':
    player = Player(SinWave())
    player.start()
    time.sleep(5)
    player.stop()
