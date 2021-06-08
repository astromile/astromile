import ipywidgets as ui

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

    def stop(self, pid=None):
        """
        Stop player with given pid. If pid is None, stop all players.
        :param pid: player id (received upon add_player() invocation)
        :return:
        """
        if pid is None:
            [player.stop() for player in self.players.values()]
        else:
            self.players[pid].stop()

    def start(self, pid=None):
        """
        Starts player with given pid. If pid is None, starts all players.
        :param pid: player id (received upon add_player() invocation)
        :return:
        """
        if pid is None:
            [player.start() for player in self.players.values()]
        else:
            self.players[pid].start()

    def set_freq(self, pid, freq):
        self.players[pid].set_freq(freq)

    class SingleToneUI(ui.VBox):
        HALFTONE = 2 ** (1 / 12)
        TONES = 36
        TONE = ['A', 'A#', 'H', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']

        def __init__(self, player, player_id, freq=440):
            self.player = player
            self.player_id = player_id
            self.base_freq = freq / 2

            self.play_checkbox = ui.Checkbox(value=False)
            self.play_checkbox.observe(self.on_play_checkbox, names='value')

            self.freq_label = ui.Label(value=f'{freq} Hz')

            self.freq_slider = ui.IntSlider(value=12, min=0, max=self.TONES, step=1,
                                            layout=ui.Layout(width='100%'))
            self.freq_slider.observe(self.set_freq, names='value')

            layout = ui.Layout(width='2.12%')
            self.freq_scala = ui.HBox([ui.Label()]
                                      + [ui.Label(value=self.TONE[i % 12], layout=layout)
                                         for i in range(self.TONES + 1)])

            super().__init__([
                ui.HBox([self.play_checkbox, self.freq_label]),
                self.freq_slider,
                self.freq_scala
            ])

        def set_freq(self, e):
            freq = self.base_freq * self.HALFTONE ** e.new
            self.player.set_freq(self.player_id, freq)
            self.freq_label.value = f'{freq} Hz'

        def on_play_checkbox(self, e):
            if e.new:
                self.player.start(self.player_id)
            else:
                self.player.stop(self.player_id)

    class UI:

        def __init__(self, blocksize=4410, buffersize=2, samplerate=44100, freq=440, tone_count=3):
            self.player = MultiTonePlayer(freq=freq, blocksize=blocksize, buffersize=buffersize, samplerate=samplerate)
            self.tones = []
            for _ in range(tone_count):
                player_id = self.player.add(freq)
                self.tones.append(MultiTonePlayer.SingleToneUI(self.player, player_id, freq))

            # if fig is None or ax is None:
            #     self.fig, self.ax = self.plt.subplots()
            # else:
            #     self.fig, self.ax = fig, ax
            # self.plot(show=False)

        def show(self):
            from IPython.display import display
            display(*self.tones)

        # def plot(self, show=True):
        #     self.ax.clear()
        #     self.ax.plot(self.player.t, np.sin(2 * np.pi * self.player.freq * self.player.t))
        #     self.ax.set_xlim(0, 1 / self.base_freq)
        #     self.ax.grid()
        #     # if show:
        #     #    self.fig.show()
