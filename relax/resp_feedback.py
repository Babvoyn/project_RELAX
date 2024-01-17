"""
This module contains the different function that enable to preprocess the 
respiratory data and to change the layer accordding to it.
"""
import time

import numpy as np
from scipy.signal import firwin, lfilter

from relax.bufferQueue import BufferQueue

RESP_BUFFER_DURATION = 10
LOWPASS_ORDER = 200
LOWPASS_CUT = 1.0


def lowpass_fir_filter(data, lowcut, sampling_rate, order):
    """
    Function that filter low frequency of input data with a
    Finite Impulse Response filter

    Parameters
    ----------
    data: Array of Float
        Data to be filtered.
    lowcut: Float
        Frequency cut of the lowpass
    sampling_rate: Float
        Sampling rate of the input data
    order: Int
        Order of the FIR filter

    Returns
    -------
    _: Array of float
        Filtered data
    """
    fir_filter = firwin(order, lowcut, pass_zero=True, scale=True, fs=sampling_rate)
    return lfilter(fir_filter, 1.0, data)


def resp_modulation(resp, buffer, sampling_rate):
    """
    Function used for offline simulation of the resp modulation e.g. the creation
    of the mock soundscape.

    Parameters
    ----------
    resp: Array of Float
        The resp data sample received by the recording
    buffer: BufferQueue
        The buffer of the resp data
    sampling_rate: Float
        Sampling rate of the input data

    Returns
    -------
    modulation: float
        Return the volume of the resp layer for the input data
    """
    # Add the data to the buffer
    buffer.add_data(resp)
    if buffer.full():
        # Lowpass filter the resp data
        filtered = lowpass_fir_filter(buffer, LOWPASS_CUT, sampling_rate, LOWPASS_ORDER)
        # Compute the mean of the filtered input data and transform it in a scale
        # where 0 is the minimum of the filtered data and 1 is the maximum
        modulation = (
            np.mean(filtered[len(filtered) - len(resp) :]) - min(filtered)
        ) / (max(filtered) - min(filtered))
        return modulation
    return -1.0


def resp_feedback(bfb, test=False):
    """
    Function called on a thread that modulate the resp layer according to the
    physiological data of the subject.

    Parameters
    ----------
    biofeedback: Biofeedback
        biofeedback instance of the current block
    test: Boolean
        If true, only modulate resp if the state is resp. Enable to only listen
        to one layer for latency test
    """
    print("Resp thread started")

    # If the state is resp we modulate the resp layer online according to the
    # current subject breathing
    if bfb.cond == "resp":
        # Init resp buffer used to compute the proportion i.e. the volume
        buffer = BufferQueue(RESP_BUFFER_DURATION * bfb.sampling_rate)
        num_smp, num_evt = bfb.ft_resp.wait(
            bfb.header_resp.nSamples, bfb.header_resp.nEvents, 500
        )
        # While we are recording data
        while bfb.recording:
            # We get the last resp data and add it to the buffer
            new_smp, new_evt = bfb.ft_resp.wait(num_smp, num_evt, 500)
            if new_smp == num_smp:
                continue
            data_sample = np.array(bfb.ft_resp.getData([num_smp, new_smp - 1])).T
            resp = data_sample[bfb.resp_pos]
            buffer.add_data(resp)
            if buffer.full():
                # The first time that the buffer is full we start the audio
                if not bfb.audio_on:
                    bfb.audio_on = True
                # Lowpass filter the resp data
                filtered = lowpass_fir_filter(
                    buffer, LOWPASS_CUT, bfb.sampling_rate, LOWPASS_ORDER
                )
                # Compute the mean of the filtered input data and transform it
                # in a scal where 0 is the minimum of the filtered data and 1 is
                # the maximum
                modulation = (
                    np.mean(filtered[len(filtered) - len(resp) :]) - min(filtered)
                ) / (max(filtered) - min(filtered))
                # The volume of the resp layer is changed
                bfb.sound_mod[2] = modulation

            num_smp = new_smp
            num_evt = new_evt
    # If the state isn't resp we modulate the resp layer according to a mock
    # shuffled and precalculated on the subject resting state breathing
    elif not test:
        last_index = 0
        mock_time = bfb.mock_time
        mock_resp = bfb.mock_resp

        # We are waiting for the audio to start to start modulate the layer
        while not bfb.audio_on:
            time.sleep(0.1)

        # While we are recording data
        while bfb.recording:
            # Get the current time in the mock modulation reference
            in_mock_time = time.time() - bfb.audio_start
            # According to this time we get the index in the mock modulation
            for i in range(last_index, len(mock_time) - 1):
                if mock_time[i] <= in_mock_time and mock_time[i + 1] > in_mock_time:
                    last_index = i
                    break
            # The volume is set at the volume of the mock at this index
            bfb.sound_mod[2] = mock_resp[last_index]
            time.sleep(0.01)
    print("Resp thread finished")
