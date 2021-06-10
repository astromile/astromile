import ipywidgets as ui
import matplotlib.pyplot as plt
import numpy as np

from astromusic.players.constampl import ConstAmplPlayer


class MultiTonePlayer:
    MAX_AMPL = 2 ** 15 - 1

    def __init__(self, blocksize=4410, buffersize=2, samplerate=44100, freq=440):
        self.blocksize = blocksize
        self.buffersize = buffersize
        self.samplerate = samplerate
        self.freq = freq

        self.next_id = 0
        self.players = {}

    def add(self, freq=None):
        freq = self.freq if freq is None else freq
        pid = self.next_id
        self.players[pid] = ConstAmplPlayer(self.blocksize, self.buffersize, self.samplerate,
                                            freq=freq)
        self.next_id += 1
        return pid

    def get(self, pid):
        return self.players[pid]

    def stop(self, pid=None, blocking=False):
        """
        Stop player with given pid. If pid is None, stop all players.
        :param pid: player id (received upon add_player() invocation)
        :param blocking: whether to block until Thread is joined
        :return:
        """
        if pid is None:
            [player.stop() for player in self.players.values()]
        else:
            self.get(pid).stop(blocking)

    def start(self, pid=None):
        """
        Starts player with given pid. If pid is None, starts all players.
        :param pid: player id (received upon add_player() invocation)
        :return:
        """
        if pid is None:
            [player.start() for player in self.players.values()]
        else:
            self.get(pid).start()

    class SingleToneUI(ui.HBox):
        HALFTONE = 2 ** (1 / 12)
        TONES = 36
        TONE = ['A', 'A#', 'H', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']

        def __init__(self, multi_player, player_id, freq=440, freq_observer=None, switch_observer=None):
            """

            :param multi_player: instance of MultiTonePlayer
            :param player_id: id of a single tone
            :param freq: initial frequency
            :param freq_observer: callback, which is invoked as freq_observer(player_id, freq) when frequency changes
            """
            self.multi_player = multi_player
            self.player_id = player_id
            self.base_freq = freq / 2
            self.freq_observer = freq_observer
            self.switch_observer = switch_observer

            self.play_checkbox = ui.Checkbox(description=f'({player_id + 1})', value=False,
                                             indent=False, layout=ui.Layout(width='5%'))
            self.play_checkbox.observe(self.on_play_checkbox, names='value')

            self.freq_label = ui.Label(value=f'{freq} Hz', layout=ui.Layout(width='7%'))

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

        def player(self):
            return self.multi_player.get(self.player_id)

        def set_freq(self, e):
            freq = self.base_freq * self.HALFTONE ** e.new
            self.player().set_freq(freq)
            self.freq_label.value = f'{round(100 * freq) / 100} Hz'
            if self.freq_observer is not None:
                self.freq_observer(self.player_id, freq)

        def on_play_checkbox(self, e):
            if e.new:
                self.player().start()
            else:
                self.player().stop(blocking=False)
            if self.switch_observer is not None:
                self.switch_observer(self.player_id, e.new)

    class UI:

        def __init__(self, blocksize=4410, buffersize=2, samplerate=44100, freq=440, tone_count=3):
            self.player = MultiTonePlayer(freq=freq, blocksize=blocksize, buffersize=buffersize, samplerate=samplerate)
            self.tones = []
            self.switch_all = ui.Checkbox(description='All', value=False)
            self.switch_all.observe(self.on_switch_all, names='value')
            for _ in range(tone_count):
                player_id = self.player.add(freq)
                self.tones.append(MultiTonePlayer.SingleToneUI(self.player, player_id, freq,
                                                               freq_observer=self.on_freq_change,
                                                               switch_observer=self.on_freq_change))

            plt.ioff()
            self.fig, self.ax = plt.subplots(figsize=[8, 3])
            self.fig.tight_layout()
            plt.ion()
            self.plot(show=False)

        # noinspection PyTypeChecker
        def show(self):
            from IPython.display import display
            if plt.get_backend() == 'module://ipympl.backend_nbagg':
                display(self.switch_all, *self.tones, self.fig.canvas)
            else:
                display(self.switch_all, *self.tones, self.fig)

        def on_switch_all(self, e):
            for tone in self.tones:
                tone.play_checkbox.value = e.new

        def on_freq_change(self, *_):
            self.plot()

        def plot(self, show=True):
            self.ax.clear()
            for tone in self.tones:
                t = tone.player().t
                freq = tone.player().freq
                style = '-' if tone.play_checkbox.value else '--'
                self.ax.plot(t, np.sin(2 * np.pi * freq * t), style,
                             label=f'{tone.play_checkbox.description} : {round(100 * freq) / 100} Hz')
            self.ax.legend(loc='upper left')
            self.ax.set_xlim(0, 4 / 220)
            self.ax.grid()
            # if show:
            #     self.fig.show()
