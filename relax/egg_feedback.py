"""
This module contains the different function that enable to preprocess the 
egg data and to change the layer accordding to it.
"""
import time

import numpy as np
from scipy.signal import firwin, lfilter
from sklearn.linear_model import LinearRegression

from relax.bufferQueue import BufferQueue

GAS_DOWN = 30
EGG_BUFFER_DURATION = 45
MED_WIN = 100
EGG_WIN = 0.015
FIR_ORDER = 2000


def bandpass_fir_filter(data, lowcut, highcut, sampling_rate, order):
    """
    Function that bandpass filter frequency of input data with a
    Finite Impulse Response filter  

    Parameters
    ----------
    data: Array of Float
        Data to be filtered.
    lowcut: Float
        Low frequency cut of the filter
    highcut: Float
        High frequency cut of the filter
    sampling_rate: Float
        Sampling rate of the input data
    order: Int
        Order of the FIR filter

    Returns
    -------
    _: Array of float
        Filtered data
    """
    fir_filter = firwin(order, [lowcut, highcut], pass_zero=False, fs=sampling_rate)
    return lfilter(fir_filter, 1.0, data)


def median_filter(data, start_from_end, window_rad):
    """
    Function that apply a median filter to the input data on the last datum with
    a given window radius

    Parameters
    ----------
    data: Array of Float
        Data to be filtered.
    start_from_end: Int
        The index to apply the filter starting from the end
    window_rad: Int
        Window radius of the median filter.

    Returns
    -------
    filtered_data: Array of float
        Filtered data
    """
    # Getting the index to apply the filter starting from the beginning
    start_index = len(data) - start_from_end
    if start_index < 0:
        start_index = 0

    filtered_data = []
    for i in range(start_index, len(data)):
        start = max(0, i - window_rad)
        end = min(len(data), i + window_rad + 1)
        filtered_data.append(np.median(data[start:end]))

    return filtered_data


def egg_modulation(
    egg,
    buffer,
    med_buffer,
    filter_buffer,
    time_abscissa,
    down_sr,
    egg_freq,
    last_mod,
    delta_t,
):
    """
    Function used for offline simulation of the egg modulation e.g. the creation
    of the mock soundscape.

    Parameters
    ----------
    egg: Array of Float
        The egg data sample received by the recording
    buffer: BufferQueue
        The downsampled buffer of the egg data
    med_buffer: BufferQueue
        The buffer of the egg data after median filter
    filter_buffer: BufferQueue
        The buffer of the egg data after bandpass filter
    time_abscissa: Array of Float
        Array of time stamp used to compute the linear regression
    down_sr: Float
        Sampling rate of the data after down sampling
    egg_freq: Float
        Peak frequency of the egg data
    last_mod: Float
        Modulation of the last egg data sample
    delta_t: Float
        Duration between two egg data sample

    Returns
    -------
    modulation: float
        Return the volume of the egg layer for the input data if the buffers are
        full. Return -1 otherwise.
    """

    # Add and downsample the egg data sample to the buffer
    down_data = buffer.add_data(egg)

    # Median filtering on the last egg datum. We recompute only the datum
    # that contain the new egg sample in their median window radius as the other
    # are not changed.
    med_filtered = median_filter(buffer, MED_WIN + len(down_data), MED_WIN)
    # Egg sample filtered
    data_to_add = med_filtered[len(med_filtered) - len(down_data) :]
    # Egg data recomputed thank to the egg sample
    data_modified = med_filtered[: len(med_filtered) - len(down_data)]
    # Apply recomputation 
    med_buffer[len(med_buffer) - len(data_modified) :] = data_modified
    # Add filtered egg data sample to the med_buffer
    med_buffer.add_data(data_to_add)

    # Removing trend by substracting a linear regression on the median filtered
    # buffer.
    model_med = LinearRegression().fit(
        time_abscissa[: len(med_buffer)].reshape(-1, 1), med_buffer
    )
    regre_med = (
        time_abscissa[: len(med_buffer)] * model_med.coef_ + model_med.intercept_
    )
    clean_med = med_buffer - regre_med

    # Filtering the med_buffer after trend removing with a FIR bandpass filter
    filtered = bandpass_fir_filter(
        clean_med,
        egg_freq - EGG_WIN,
        egg_freq + EGG_WIN,
        down_sr,
        FIR_ORDER,
    )

    # We add the median trend and bandpass filtered egg sample to the
    # filter_buffer. With the exception of the first time the buffer is full.
    # In this case we set the entire filter_buffer with the entire output of
    # the bandpass to clean the previous sample that have been miscalculated.
    if (
        len(filter_buffer) < filter_buffer.max_len
        and len(filter_buffer) + len(down_data) >= filter_buffer.max_len
    ):
        filter_buffer[filter_buffer.max_len :] = filtered
    else:
        filter_buffer.add_data(filtered[-len(down_data) :])

    if filter_buffer.full():
        # Compute the mean of the filtered input data and transform it in a scale
        # where 0 is the minimum of the filtered data and 1 is the maximum
        modulation = (
            np.mean(filter_buffer[len(filter_buffer) - len(down_data) :])
            - min(filter_buffer)
        ) / (max(filter_buffer) - min(filter_buffer))

        # We make sure that modulation difference since the last modulation isn't
        # too much according to the egg max frequency maximum variation
        if last_mod != -1.0: # Is False only fo the first calculated mod
            max_egg_freq = egg_freq + EGG_WIN
            max_change = 2 * np.pi * max_egg_freq * delta_t
            max_mod = last_mod + max_change
            min_mod = last_mod - max_change
            # We saturate the change to this maximum change
            modulation = min(modulation, max_mod)
            modulation = max(modulation, min_mod)
        return modulation
    else:
        return -1.0


def egg_feedback(biofeedback, test=False):
    """
    Function called on a thread that modulate the egg layer according to the
    physiological data of the subject.

    Parameters
    ----------
    biofeedback: Biofeedback
        biofeedback instance of the current block
    test: Boolean
        If true, only modulate resp if the state is resp. Enable to only listen
        to one layer for latency test
    """
    print("Egg thread started")
    # If the state is egg we modulate the egg layer online according to the
    # current subject egg
    if biofeedback.cond == "egg":
        # Init last_mod for maximum change saturation
        last_mod = -1.0
        # Compute the sampling rate after downsampling
        down_sr = biofeedback.sampling_rate / GAS_DOWN
        # Size of the buffer according to the new sampling rate
        len_buffer = int(EGG_BUFFER_DURATION * down_sr)
        # Init the different buffer
        buffer = BufferQueue(len_buffer, down=GAS_DOWN)
        med_buffer = BufferQueue(len_buffer)
        filter_buffer = BufferQueue(len_buffer)

        time_abscissa = np.array([x / down_sr for x in range(len_buffer)])
        num_smp, num_evt = biofeedback.ft_egg.wait(
            biofeedback.header_egg.nSamples, biofeedback.header_egg.nEvents, 500
        )

        # While we are recording data
        while biofeedback.recording:
            # We get the last egg data
            new_smp, new_evt = biofeedback.ft_egg.wait(num_smp, num_evt, 500)
            if new_smp == num_smp:
                continue
            data_sample = biofeedback.ft_egg.getData([num_smp, new_smp - 1]).T
            egg = data_sample[int(biofeedback.egg_pos)]

            # Add and downsample the egg data sample to the buffer
            down_data = buffer.add_data(egg)

            # We make sure that after downsample we at least added a datum to the
            # buffer
            if len(down_data) > 0:

                # Median filtering on the last egg datum. We recompute only the
                # datum that contain the new egg sample in their median window
                # radius as the other are not changed.
                med_filtered = median_filter(buffer, MED_WIN + len(down_data), MED_WIN)
                # Egg sample filtered
                data_to_add = med_filtered[len(med_filtered) - len(down_data) :]
                # Egg data recomputed thank to the egg sample
                data_modified = med_filtered[: len(med_filtered) - len(down_data)]
                # Apply recomputation 
                med_buffer[len(med_buffer) - len(data_modified) :] = data_modified
                # Add filtered egg data sample to the med_buffer
                med_buffer.add_data(data_to_add)

                # Removing trend by substracting a linear regression on the
                # median filtered buffer.
                model_med = LinearRegression().fit(
                    time_abscissa[: len(med_buffer)].reshape(-1, 1), med_buffer
                )
                regre_med = (
                    time_abscissa[: len(med_buffer)] * model_med.coef_
                    + model_med.intercept_
                )
                clean_med = med_buffer - regre_med

                # Filtering the med_buffer after trend removing with a FIR
                # bandpass filter
                filtered = bandpass_fir_filter(
                    clean_med,
                    float(biofeedback.egg_freq) - EGG_WIN,
                    float(biofeedback.egg_freq) + EGG_WIN,
                    down_sr,
                    FIR_ORDER,
                )

                # We add the median trend and bandpass filtered egg sample to the
                # filter_buffer. With the exception of the first time the buffer
                # is full. In this case we set the entire filter_buffer with the
                # entire output of the bandpass to clean the previous sample that
                # have been miscalculated.
                if (
                    len(filter_buffer) < filter_buffer.max_len
                    and len(filter_buffer) + len(down_data) >= filter_buffer.max_len
                ):
                    filter_buffer[filter_buffer.max_len :] = filtered
                else:
                    filter_buffer.add_data(filtered[-len(down_data) :])

                if filter_buffer.full():
                    # The first time that the buffer is full we start the audio
                    if not biofeedback.audio_on:
                        biofeedback.audio_on = True

                    # Compute the mean of the filtered input data and transform
                    # it in a scale where 0 is the minimum of the filtered data
                    # and 1 is the maximum
                    modulation = (
                        np.mean(filter_buffer[len(filter_buffer) - len(down_data) :])
                        - min(filter_buffer)
                    ) / (max(filter_buffer) - min(filter_buffer))

                    # We make sure that modulation difference since the last
                    # modulation isn't too much according to the egg max frequency
                    # maximum variation
                    if last_mod != -1.0: # Is False only fo the first calculated mod
                        max_egg_freq = float(biofeedback.egg_freq) + EGG_WIN
                        delta_t = len(egg) * biofeedback.sampling_rate
                        max_change = 2 * np.pi * max_egg_freq * delta_t
                        max_mod = last_mod + max_change
                        min_mod = last_mod - max_change
                        # We saturate the change to this maximum change
                        modulation = min(modulation, max_mod)
                        modulation = max(modulation, min_mod)
                    last_mod = modulation

                    # Update egg volume
                    biofeedback.sound_mod[0] = modulation

            num_smp = new_smp
            num_evt = new_evt
    # If the state isn't resp we modulate the resp layer according to a mock
    # shuffled and precalculated on the subject resting state breathing
    elif not test:
        last_index = 0
        mock_time = biofeedback.mock_time
        mock_egg = biofeedback.mock_egg

        # We are waiting for the audio to start to start modulate the layer
        while not biofeedback.audio_on:
            time.sleep(0.1)

        # While we are recording data
        while biofeedback.recording:
            # Get the current time in the mock modulation reference
            in_mock_time = time.time() - biofeedback.audio_start
            # According to this time we get the index in the mock modulation
            for i in range(last_index, len(mock_time) - 1):
                if mock_time[i] <= in_mock_time and mock_time[i + 1] > in_mock_time:
                    last_index = i
                    break
            # The volume is set at the volume of the mock at this index
            biofeedback.sound_mod[0] = mock_egg[last_index]
            time.sleep(0.01)
    print("Egg thread finished")
