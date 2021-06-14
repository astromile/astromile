import ipywidgets as ui
import matplotlib.pyplot as plt
import numpy as np

from astromusic.players.constampl import VariableWave
from astromusic.players.player import Player, Wave


class SingleToneUI(ui.HBox):
    HALFTONE = 2 ** (1 / 12)
    TONES = 36
    TONE = ['A', 'A#', 'H', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']

    def __init__(self, wave_id, wave, base_freq=220, freq_observer=None, switch_observer=None):
        self.wave_id = wave_id
        self.wave = wave
        self.base_freq = base_freq
        self.freq_observer = freq_observer
        self.switch_observer = switch_observer

        self.play_checkbox = ui.Checkbox(description=f'({self.wave_id + 1})', value=False,
                                         indent=False, layout=ui.Layout(width='5%'))
        self.play_checkbox.observe(self.on_play_checkbox, names='value')

        self.freq_label = ui.Label(value=f'{self.wave.freq} Hz', layout=ui.Layout(width='7%'))

        self.freq_slider = ui.IntSlider(value=12, min=0, max=self.TONES, step=1,
                                        layout=ui.Layout(width='100%', margin='0px'))
        self.freq_slider.observe(self.set_freq, names='value')

        layout = ui.Layout(width='2.47%', margin='0px', display='flex', justify_content='center')
        self.freq_scala = ui.HBox([ui.Label(value=self.TONE[i % 12], layout=layout) for i in range(self.TONES + 1)])

        super().__init__([
            self.play_checkbox,
            self.freq_label,
            ui.VBox([self.freq_slider, self.freq_scala],
                    layout=ui.Layout(width='88%'))
        ])

    def is_on(self):
        return self.play_checkbox.value

    def switch(self, on):
        self.play_checkbox.value = on

    def on_play_checkbox(self, e):
        # if e.new:
        #     self.player.start()
        # else:
        #     self.player.stop(blocking=False)
        if self.switch_observer is not None:
            self.switch_observer(self.wave_id, e.new)

    def set_freq(self, e):
        freq = self.base_freq * self.HALFTONE ** e.new
        self.wave.set_freq(freq)
        self.freq_label.value = f'{round(100 * freq) / 100} Hz'
        if self.freq_observer is not None:
            self.freq_observer(self.wave_id, freq)


class UI(ui.VBox):
    def __init__(self, blocksize=4410, buffersize=2, samplerate=44100, freq=440, tone_count=3):
        self.switch_all = ui.Checkbox(description='All', value=False)
        self.switch_all.observe(self.on_switch_all, names='value')

        self.tones = []
        self.players = []
        for i in range(tone_count):
            wave = VariableWave(freq=freq)
            player = Player(wave, blocksize=blocksize, buffersize=buffersize, samplerate=samplerate)
            widget = SingleToneUI(i, wave, freq_observer=self.on_freq_change, switch_observer=self.on_player_switch)
            self.players.append(player)
            self.tones.append(widget)

        plt.ioff()
        self.fig, self.ax = plt.subplots(figsize=[8, 3])
        self.fig.tight_layout()
        plt.ion()
        self.plot()

        fig = self.fig if plt.get_backend() == 'nbAgg' else self.fig.canvas
        super().__init__([
            self.switch_all,
            *self.tones,
            fig
        ])

    def on_switch_all(self, e):
        [tone.switch(e.new) for tone in self.tones]

    def on_freq_change(self, *_):
        self.plot()

    def on_player_switch(self, wave_id, on):
        if on:
            self.players[wave_id].start()
        else:
            self.players[wave_id].stop(blocking=False)
        self.plot()

    def plot(self):
        self.ax.clear()
        for widget, player in zip(self.tones, self.players):
            t = player.t
            freq = widget.wave.freq
            style = '-' if widget.is_on() else '--'
            self.ax.plot(t, np.sin(2 * np.pi * freq * t), style,
                         label=f'{widget.play_checkbox.description} : {round(100 * freq) / 100} Hz')
        self.ax.legend(loc='upper left')
        self.ax.set_xlim(0, 4 / 220)
        self.ax.grid()


class MultiWave(Wave):

    def __init__(self, *waves):
        self.waves = waves

    def wave(self, t):
        signal = super().wave(t)
        for wave in self.waves:
            signal += wave.wave(t)
        signal /= len(self.waves)
        return signal


class MergedWaveUI(ui.VBox):
    def __init__(self, blocksize=4410, buffersize=2, samplerate=44100, freq=440, tone_count=3):
        self.switch_all = ui.Checkbox(description='All', value=False)
        self.switch_all.observe(self.on_switch_all, names='value')

        self.tones = []
        self.waves = []
        for i in range(tone_count):
            wave = VariableWave(freq=freq, amplitude=0.0)
            widget = SingleToneUI(i, wave, freq_observer=self.on_freq_change, switch_observer=self.on_player_switch)
            self.waves.append(wave)
            self.tones.append(widget)

        self.display_wave = MultiWave(*[VariableWave(freq=freq, amplitude=1.0) for _ in range(tone_count)])
        self.player = Player(MultiWave(*self.waves), blocksize=blocksize, buffersize=buffersize, samplerate=samplerate)
        self.player.start()

        plt.ioff()
        self.fig, self.ax = plt.subplots(nrows=2, ncols=1, figsize=[8, 3])
        self.fig.tight_layout()
        plt.ion()
        self.plot()

        fig = self.fig if plt.get_backend() == 'nbAgg' else self.fig.canvas
        super().__init__([
            self.switch_all,
            *self.tones,
            fig
        ])

    def __del__(self):
        self.player.stop(blocking=False)

    def on_switch_all(self, e):
        [tone.switch(e.new) for tone in self.tones]

    def on_freq_change(self, wave_id, freq):
        self.plot()

    def on_player_switch(self, wave_id, on):
        self.waves[wave_id].set_amplitude(float(on))
        self.plot()

    def plot(self):
        for ax in self.ax:
            ax.clear()
        ax = self.ax[0]
        for i, widget in enumerate(self.tones):
            t = self.player.t
            wave = self.display_wave.waves[i]
            wave.freq = widget.wave.freq
            wave.amplitude = 1.0
            wave.phase = widget.wave.phase
            style = '-' if widget.is_on() else '--'
            ax.plot(t, wave.wave(t), style,
                    label=f'{widget.play_checkbox.description} : {round(100 * widget.wave.freq) / 100} Hz')

            wave.amplitude = widget.wave.amplitude
        ax.legend(loc='upper left')
        ax.set_xlim(0, 4 / 220)
        ax.grid()

        ax = self.ax[1]
        ax.plot(t, self.display_wave.wave(t))
        ax.set_xlim(0, 4 / 200)
        ax.grid()
