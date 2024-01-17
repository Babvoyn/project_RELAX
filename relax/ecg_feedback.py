"""
This module contains the different function that enable to preprocess the ecg
data and to change the layer accordding to it.
"""
import os
import random
import time
import wave
from math import floor

import numpy as np
from relax.bufferQueue import BufferQueue

# Duration in second of the ecg buffer queue
ECG_BUFFER_DURATION = 2


def get_random_file(folder):
    """
    Function that return the path of a random file inside a folder

    Parameters
    ----------
    folder: String
        Path to the folder in which a file will be chose from.

    Returns
    -------
    _: String
        Path of a random file inside the specified folder
    """
    file = random.choice(os.listdir(folder))
    return folder + "/" + file


def get_random_wav(folder):
    """
    Function that return a wav instance of a random wav file inside a folder

    Parameters
    ----------
    folder: String
        Path to the folder in which the wav will be chose from.

    Returns
    -------
    _: wav
        wav instance of a random wav file inside the specified folder
    """
    return wave.open(get_random_file(folder), "rb")


def get_ecg_wav(biofeedback):
    """
    Function that return a random wav instance of the current sound being played
    in the ecg layer

    Parameters
    ----------
    biofeedback: Biofeedback
        biofeedback instance of the current block

    Returns
    -------
    _: wav
        Random wav instance of current sound
    """
    # Reformating variable name
    sc_dur = biofeedback.SOUNDSCAPE_DURATION

    # Get the index of the current sound being played
    if biofeedback.audio_start == 0:
        index = 0
    else:
        t_point = time.time() - biofeedback.audio_start
        index = floor(t_point / sc_dur)

    # Get the folder of the current sound being played
    folder = biofeedback.soundscapes_folder[index]
    root = biofeedback.root

    return get_random_wav(root +'/'+folder + "/ecg")


def ecg_modulation(ecg, last_ecg_point, buffer, last_time, now):
    """
    Function used for offline simulation of the ecg modulation e.g. the creation
    of the mock soundscape.

    Parameters
    ----------
    ecg: Array of Float
        The ecg data sample received by the recording
    last_ecg_point: Float
        Latest ecg point before the ecg sample. It's used to compute a derivative
        with the same length as ecg.
    buffer: BufferQueue
        The buffer of the resp data
    last_time: Float
        The last time as heart beat have been detected
    now: Float
        The current time

    Returns
    -------
    _: Float
        If a heart beat is detected return now
        Else return last_time
    """
    # First we derivate the data and add it to the buffer
    d_ecg = np.diff([last_ecg_point] + ecg)
    buffer.add_data(d_ecg)
    if buffer.full():
        if len(d_ecg) > 0:
            # We take the min of the derivative of the last sample and
            # compare it to the whole buffer
            min_decg = min(d_ecg)
            prop = buffer.prop(min_decg)
            # If this min is in the lowest 20% of the buffer and that it has
            # been more than 0.5s that a heart beat have been detected then
            # we conclude that a heart beat is occuring
            if prop < 0.2 and now - last_time > 0.5:
                return now
    return last_time


def ecg_feedback(biofeedback, test=False):
    """
    Function called on a thread that modulate the ecg layer according to the
    physiological data of the subject.

    Parameters
    ----------
    biofeedback: Biofeedback
        biofeedback instance of the current block
    test: Boolean
        If true, only modulate ecg if the state is ecg. Enable to only listen to
        one layer for latency test
    """
    print("Ecg thread started")

    # If the state is ecg we modulate the ecg layer online according to the
    # current subject ecg
    if biofeedback.cond == "ecg":

        # We preload the wav to reduce latency when a heart beat is detected
        biofeedback.ecg_wavs = [get_ecg_wav(biofeedback), get_ecg_wav(biofeedback)]
        buffer = BufferQueue(ECG_BUFFER_DURATION * biofeedback.sampling_rate)
        last_ecg_point = 0
        last_time = time.time()
        num_smp, num_evt = biofeedback.ft_ecg.wait(
            biofeedback.header_ecg.nSamples, biofeedback.header_ecg.nEvents, 500
        )

        # While we are recording data
        while biofeedback.recording:

            # We get the last ecg data
            new_smp, new_evt = biofeedback.ft_ecg.wait(num_smp, num_evt, 500)
            if new_smp == num_smp:
                continue
            data_sample = np.array(biofeedback.ft_ecg.getData([num_smp, new_smp - 1])).T
            ecg = (
                data_sample[biofeedback.ecg_poses[0]]
                - data_sample[biofeedback.ecg_poses[1]]
            )

            # First we derivate the data and add it to the buffer
            d_ecg = np.diff([last_ecg_point] + ecg)
            last_ecg_point = ecg[-1]
            buffer.add_data(d_ecg)

            if buffer.full():
                # The first time that the buffer is full we start the audio
                if not biofeedback.audio_on:
                    biofeedback.audio_on = True

                # We take the min of the derivative of the last sample and
                # compare it to the whole buffer
                min_decg = min(d_ecg)
                prop = buffer.prop(min_decg)

                # If this min is in the lowest 20% of the buffer and that it has
                # been more than 0.5s that a heart beat have been detected then
                # we conclude that a heart beat is occuring
                if prop < 0.2 and time.time() - last_time > 0.4:
                    last_time = time.time()
                    old_index = biofeedback.ecg_index
                    # Change ecg_index to read a new file
                    biofeedback.ecg_index = (biofeedback.ecg_index + 1) % 2
                    # Record heart beat timestamp
                    last_time = time.time()
                    biofeedback.ecg_ts.append(last_time)
                    # Load next ecg wav
                    biofeedback.ecg_wavs[old_index] = get_ecg_wav(biofeedback)

            num_smp = new_smp
            num_evt = new_evt

    # If the state isn't ecg we modulate the ecg layer according to a mock
    # shuffled and precalculated on the subject resting state ecg
    elif not test:
        biofeedback.ecg_wavs = [get_ecg_wav(biofeedback), get_ecg_wav(biofeedback)]
        last_index = 0
        new_index = 0
        mock_time = biofeedback.mock_time
        mock_ecg = biofeedback.mock_ecg

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
                    new_index = i
                    break
            # If there is a heart beat between this index and the last one we
            # checked we start a new sound
            if 1 in mock_ecg[last_index:new_index]:
                old_index = biofeedback.ecg_index
                biofeedback.ecg_index = (biofeedback.ecg_index + 1) % 2
                biofeedback.ecg_ts.append(time.time())
                biofeedback.ecg_wavs[old_index] = get_ecg_wav(biofeedback)
            last_index = new_index
            time.sleep(0.01)
    print("Ecg thread finished")
