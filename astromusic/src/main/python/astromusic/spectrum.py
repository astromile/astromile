import numpy as np
import scipy.fft


class Harmonics:
    def __init__(self, freqs, amplitudes):
        self.freqs = np.array(freqs)
        self.amplitudes = np.array(amplitudes)

    def factors(self):
        return np.round(self.freqs / self.freqs[0]).astype(int)

    def base_freq(self):
        return np.sum(self.amplitudes * self.freqs / self.factors()) / self.amplitudes.sum()


class Spectrum:
    def __init__(self, freqs, amplitudes):
        self.freqs = freqs
        self.amplitudes = amplitudes

    def harmonics(self, eps=10.0, k=0.1):
        f, a = self.freqs, self.amplitudes
        m = a > a.max() * k
        f = f[m]
        a = a[m]
        i = 0
        n = len(f)
        freqs, amplitudes = [], []
        while i < n:
            j = i + 1
            while j < n and f[j] <= f[j - 1] + eps:
                j += 1
            amax = a[i:j].max()
            # print(i, j, amax, f[i:j], a[i:j])
            freqs.append(f[i:j][a[i:j] == amax].mean())
            amplitudes.append(amax)
            i = j

        return Harmonics(freqs, amplitudes)

    @staticmethod
    def of(wave, fps, bytes_per_sample=2):
        """

        :param wave: actual wave data, which is further normalized to [-1, 1)
        :param fps: frames per second, a.k.a. sample rate
        :param bytes_per_sample: size of a sample used for normalization purposes, defaults to 2
        :return: Spectrum instance
        """
        dt = 1.0 / fps
        n = len(wave)
        wave_normed = wave / 2 ** (8 * bytes_per_sample - 1)
        fft = abs(scipy.fft.fft(wave_normed))
        freqs = scipy.fft.fftfreq(n, dt)
        return Spectrum(freqs[:n // 2], fft[:n // 2])
