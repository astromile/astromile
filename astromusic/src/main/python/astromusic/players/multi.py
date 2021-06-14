import ipywidgets as ui
import matplotlib.pyplot as plt
import numpy as np

from astromusic.players.constampl import VaryFreqWave
from astromusic.players.player import Player


class SingleTonePlayer:
    def __init__(self, player_id, wave, player):
        self.player_id = player_id
        self.wave = wave
        self.player = player

    def start(self):
        return self.player.start()

    def stop(self, blocking):
        return self.player.stop(blocking)

    def set_freq(self, freq):
        return self.wave.set_freq(freq)

    class UI(ui.HBox):
        HALFTONE = 2 ** (1 / 12)
        TONES = 36
        TONE = ['A', 'A#', 'H', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']

        def __init__(self, player, base_freq=220, freq_observer=None, switch_observer=None):
            self.player = player
            self.base_freq = base_freq
            self.freq_observer = freq_observer
            self.switch_observer = switch_observer

            self.play_checkbox = ui.Checkbox(description=f'({self.player.player_id + 1})', value=False,
                                             indent=False, layout=ui.Layout(width='5%'))
            self.play_checkbox.observe(self.on_play_checkbox, names='value')

            self.freq_label = ui.Label(value=f'{self.player.wave.freq} Hz', layout=ui.Layout(width='7%'))

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

        def on_play_checkbox(self, e):
            if e.new:
                self.player.start()
            else:
                self.player.stop(blocking=False)
            if self.switch_observer is not None:
                self.switch_observer(self.player.player_id, e.new)

        def set_freq(self, e):
            freq = self.base_freq * self.HALFTONE ** e.new
            self.player.set_freq(freq)
            self.freq_label.value = f'{round(100 * freq) / 100} Hz'
            if self.freq_observer is not None:
                self.freq_observer(self.player.player_id, freq)


class UI(ui.VBox):
    def __init__(self, blocksize=4410, buffersize=2, samplerate=44100, freq=440, tone_count=3):
        self.switch_all = ui.Checkbox(description='All', value=False)
        self.switch_all.observe(self.on_switch_all, names='value')

        self.tones = []
        for i in range(tone_count):
            wave = VaryFreqWave(freq=freq)
            player = SingleTonePlayer(i, wave,
                                      Player(wave, blocksize=blocksize, buffersize=buffersize, samplerate=samplerate))
            widget = player.UI(player, freq_observer=self.on_freq_change, switch_observer=self.on_freq_change)
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
        for tone in self.tones:
            tone.play_checkbox.value = e.new

    def on_freq_change(self, *_):
        self.plot()

    def plot(self):
        self.ax.clear()
        for tone in self.tones:
            t = tone.player.player.t
            freq = tone.player.wave.freq
            style = '-' if tone.play_checkbox.value else '--'
            self.ax.plot(t, np.sin(2 * np.pi * freq * t), style,
                         label=f'{tone.play_checkbox.description} : {round(100 * freq) / 100} Hz')
        self.ax.legend(loc='upper left')
        self.ax.set_xlim(0, 4 / 220)
        self.ax.grid()
