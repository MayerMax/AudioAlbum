import hashlib
import numpy as np
import matplotlib.mlab as mlab
import scipy.ndimage.morphology as image
from scipy.ndimage import maximum_filter


# np.set_printoptions(threshold=np.inf)

class FingerPrint:
    def __init__(self):
        self.default_frame_rate = 44100
        self.fft_window_size = 4096  # length of the windowing segment
        self.overlap_ratio = 0.5
        # minimum amplitude in spectrogram to be defined as a peak
        self.minimum_peak = 10
        # minimum pairing value
        self.default_merging_value = 15

        # minimum value in ms to start hashing
        self.minimum_time = 0
        # maximum value in ms to end hashing
        self.maximum_time = 200

    # channel_samples - raw data from data zone in format
    # Fs - frames per seconds for FFT transforming
    # noverlap - number of points of overlap between blocks
    # NFFT - number of data points used in each block for the FFT
    def apply_fft_trasnform(self, channel_samples):
        plot = mlab.specgram(
            channel_samples,
            Fs=self.default_frame_rate,
            NFFT=self.fft_window_size,
            noverlap=int(self.fft_window_size * 0.5),
            window=mlab.window_hanning,

        )[0]  # returns the spectrum

        plot = 10 * np.log10(plot)  # applying transformation for it
        # read here for reminding
        # https://habrahabr.ru/company/yandex/blog/270765/
        plot[plot == -np.inf] = 0
        print(plot)
        return plot

    @staticmethod
    def binary_structure(rank, connectivity):
        structure = image.generate_binary_structure(rank, connectivity)
        return structure

    # dilating binary structure with itself
    @staticmethod
    def extension_for_two_dimension(structure, iterations=20):
        iterative_structure = image.iterate_structure(
            structure=structure,
            iterations=iterations
        )
        return iterative_structure

    def get_peaks(self, channel_samples):
        plot = self.apply_fft_trasnform(channel_samples)
        structure = FingerPrint.binary_structure(2, 1)
        neighbours = FingerPrint.extension_for_two_dimension(structure)

        local_maximums = maximum_filter(plot, footprint=neighbours) == plot
        back_side = (plot == 0)
        eroded_back_side = image.binary_erosion(
            back_side,
            structure=neighbours,
            border_value=1)

        peaks = local_maximums - eroded_back_side
        real_peaks = plot[peaks]

        # same as np.nonzero(1)
        time, frequency = np.where(peaks)
        real_peaks = real_peaks.flatten()
        values = zip(frequency, time, real_peaks)

        filtered_values = [triple for triple in values if
                           triple[2] > self.minimum_peak]

        frequency_idx = [triple[1] for triple in filtered_values]
        time_idx = [triple[0] for triple in filtered_values]

        # now this amplitudes become useless and only thing we need to know
        # is when and with what frequency it has appeared
        return list(zip(frequency_idx, time_idx))  # frequency - 0 and time - 1

    def hashing_fingerprints(self, peaks):
        merge_value = self.default_merging_value
        for i in range(len(peaks)):
            for j in range(1, merge_value):
                if i + j < len(peaks):
                    first_freq = peaks[i][0]  # frequency
                    second_frequency = peaks[i + j][0]  # second frequency

                    start_time = peaks[i][1]  # first time
                    end_time = peaks[i + j][1]  # end time

                    difference = end_time - start_time
                    if self.minimum_time <= difference <= self.maximum_time:
                        result_string = str(first_freq) + \
                                        str(second_frequency) + \
                                        str(difference)

                        hashing = hashlib.sha224(
                            result_string.encode("utf-8")).hexdigest()

                        yield (hashing, start_time)
