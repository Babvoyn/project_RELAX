"""
Module to create mock volume modulation of the different layers according to the
resting state data
"""
import json
import os
from datetime import date
from pathlib import Path
from random import randint

import click
import mne
import numpy as np
from alive_progress import alive_bar

from relax.bufferQueue import BufferQueue
from relax.ecg_feedback import ECG_BUFFER_DURATION, ecg_modulation
from relax.egg_feedback import EGG_BUFFER_DURATION, GAS_DOWN, egg_modulation
from relax.resp_feedback import RESP_BUFFER_DURATION, resp_modulation

SAMP_FREQ = 64


def get_half_crossing(data, padding):
    """
    Function that return the index of the points in the input data that cross
    the 0.5 during a decreasing phase.

    Parameters
    ----------
    data: Array of Float
        Computed volume of a layer of the resting state
    padding: Int
        How much point before the computated point is used to know if we are in
        a decreasing phase
    Returns
    -------
    crossing_points: Array of Int
        Index of the points in the input data that cross the 0.5 during a
        decreasing phase
    """
    crossing_points = []
    for i in range(padding, len(data)):
        if (
            data[i - 1] > 0.5
            and data[i] <= 0.5
            and np.mean(data[i - padding : i]) > 0.5
        ):
            crossing_points.append(i)
    return crossing_points


def get_recomposed_mock(data, n_recomposed, padding=128):
    """
    Function that return shuffle volume array cut in 0.5 crossing.

    Parameters
    ----------
    data: Array of Float
        Computed volume of a layer of the resting state
    n_recomposed: Int
        How much shuffled volume to return
    padding: Int
        The padding used to get 0.5 crossing

    Returns
    -------
    recomposed_mock: Array of size n_recomposed of Array of Float
        Array of shuffled volume array
    """
    recomposed_mock = []
    crossing_points = get_half_crossing(data, padding)
    pstart = crossing_points[0]
    pend = crossing_points[-1]
    for _ in range(n_recomposed):
        pmid = crossing_points[randint(2, len(crossing_points) - 2)]
        recomposed = data[:pstart] + data[pmid:pend] + data[pstart:pmid] + data[pend:]
        recomposed_mock.append(recomposed)
    return recomposed_mock


def add_recomposed_mock_to_dict(dict_):
    """
    Function that add shuffle volume array in a dictionary.

    Parameters
    ----------
    dict_: Dictionaty
        Dictionary containing the computed volume of the different layers of the
        subject resting state
    """
    for key in ["ecg_or", "egg_or", "resp_or"]:
        data = dict_[key]
        if key == "ecg_or":
            padding = 1
        else:
            padding = 128
        recomposed_mock = get_recomposed_mock(data, 4, padding)
        for i, shuffle_volume in enumerate(recomposed_mock):
            dict_[key.replace("_or", "_" + str(i + 1))] = shuffle_volume


def get_resp_modulation(sfreq, resp_data):
    """
    Function that return volume accross time for resp data input.

    Parameters
    ----------
    sfreq: Float
        sampling frequency of the resp data
    resp_data: Array of Float
        resp data array

    Returns
    -------
    mod_array: Array of Float
        volume accross time of the input resp_data
    """
    mod_array = []
    # Get the size of a sample according to SAMP_FREQ
    samp_size = int(sfreq / SAMP_FREQ)
    buffer = BufferQueue(RESP_BUFFER_DURATION * sfreq)
    index_list = np.arange(0, len(resp_data), samp_size)
    with alive_bar(len(index_list)) as progress_bar:
        for index in index_list:
            # Get sample
            resp = resp_data[index : index + samp_size]
            if len(resp) > 0:
                # Get the sample volume
                mod = resp_modulation(resp, buffer, sfreq)
                if mod != -1.0: # Is false when the buffer isn't full
                    mod_array.append(mod)
            progress_bar()
    return mod_array


def get_egg_modulation(sfreq, egg_data, egg_freq):
    """
    Function that return volume accross time for egg data input.

    Parameters
    ----------
    sfreq: Float
        sampling frequency of the egg data
    egg_data: Array of Float
        egg data array
    egg_freq: Float
        Peak frequency of the egg data

    Returns
    -------
    mod_array: Array of Float
        volume accross time of the input egg_data
    """
    mod_array = []
    last_mod = -1
    # Get the size of a sample according to SAMP_FREQ
    samp_size = int(sfreq / SAMP_FREQ)
    # Get the sanpling rate after down sampling
    down_sr = sfreq / GAS_DOWN
    len_buffer = int(EGG_BUFFER_DURATION * down_sr)
    buffer = BufferQueue(len_buffer, down=GAS_DOWN)
    med_buffer = BufferQueue(len_buffer)
    filter_buffer = BufferQueue(len_buffer)
    time_abscissa = np.array([x / down_sr for x in range(len_buffer)])
    index_list = np.arange(0, len(egg_data), samp_size)
    with alive_bar(len(index_list)) as progress_bar:
        for index in index_list:
            # Get sample
            egg = egg_data[index : index + samp_size]
            i = int(index / samp_size)
            if len(egg) > 0:
                # Get sample volume
                mod = egg_modulation(
                    egg,
                    buffer,
                    med_buffer,
                    filter_buffer,
                    time_abscissa,
                    down_sr,
                    egg_freq,
                    last_mod,
                    1 / SAMP_FREQ,
                )
                if mod != -1.0: # Is false when the buffer isn't full
                    mod_array.append(mod)
                last_mod = mod
            progress_bar()
    return mod_array


def get_ecg_modulation(sfreq, ecg_data):
    """
    Function that return volume accross time for ecg data input.

    Parameters
    ----------
    sfreq: Float
        sampling frequency of the ecg data
    ecg_data: Array of Float
        ecg data array

    Returns
    -------
    mod_array: Array of Int
        heart beat detection accross time for the input ecg_data. 1 indicate that
        a heart beat occured at this time stamp and 0 otherwise.
    """
    heart_beat = []
    # Get the size of a sample according to SAMP_FREQ
    samp_size = int(sfreq / SAMP_FREQ)
    last_time = 0
    last_ecg_point = 0
    buffer = BufferQueue(ECG_BUFFER_DURATION * sfreq)
    index_list = np.arange(0, len(ecg_data), samp_size)
    with alive_bar(len(index_list)) as progress_bar:
        for index in index_list:
            # Get sample
            ecg = ecg_data[index : index + samp_size]
            if len(ecg) > 0:
                # Get time of last heart beat
                time = ecg_modulation(
                    ecg, last_ecg_point, buffer, last_time, index / sfreq
                )
                # If time is different than last time then a heart beat was
                # detected so we add 1
                if time != last_time:
                    last_time = time
                    heart_beat.append(1)
                else:
                    heart_beat.append(0)
                last_ecg_point = ecg[-1]
            progress_bar()
    return heart_beat


def create_mock_soundscapes(subject_id, egg_electrod, egg_freq):
    """
    Create shuffle mock soundscape modulations according to data from a resting
    state.

    Parameters
    ----------
    subject_id: String
        unique string id of the subject. It should be the same as the one
        used for recording the baseline.
    egg_electrod: Int
        index of the egg electrod that will be used to do the sound
        modulation in the fieldtrip config file.
    egg_freq: Float
        peak frequency of previously selected egg electrod.
    day: String
        Day of the desire resting state mock computation.
    """
    # Get the folder were resting state are saved
    record_folder = Path(__file__).parent / "../Data/RestingState"
    file_list = os.listdir(record_folder)
    # Get the expected file according to the day and the subject
    expected_file = f"RELAX_sub-{subject_id}_RestingState.fif"
    if expected_file in file_list:
        print("Resting state file founded.")
        raw = mne.io.Raw(str(record_folder / expected_file))
        sfreq = raw.info["sfreq"]
        # Get the different physiological data
        resp_data = raw.get_data(["Resp"])[0]
        ecg_data = raw.get_data(["EGG2"])[0] - raw.get_data(["EGG8"])[0]
        egg_data = raw.get_data([f"EGG{egg_electrod}"])[0]
        # Get the volume of these data
        ecg_mod = get_ecg_modulation(sfreq, ecg_data)
        resp_mod = get_resp_modulation(sfreq, resp_data)
        egg_mod = get_egg_modulation(sfreq, egg_data, egg_freq)
        # Add it to a dictionary
        dict_ = {
            "subject_id": subject_id,
            "ecg_or": ecg_mod,
            "resp_or": resp_mod,
            "egg_or": egg_mod,
            "time": [x / SAMP_FREQ for x in range(len(ecg_mod))],
        }
        # Add shuffle volume to this dictionary
        add_recomposed_mock_to_dict(dict_)
        # Save it
        save_file = f"RELAX_sub-{subject_id}_PremodulatedSignal.json"
        with open(str(record_folder / save_file), "w") as f:
            json.dump(dict_, f)
    else:
        print(f"{expected_file} was not found.")


@click.command()
@click.option("--subject_id", prompt="Subject id")
@click.option("--egg_electrod", type=int, prompt="Egg electrod")
@click.option("--egg_freq", type=float, prompt="Egg freq")
def wrapper_create_mock_soundscape(subject_id, egg_electrod, egg_freq):
    """
    Wrapper to create shuffle mock soundscape modulations according to data from a resting
    state.

    Parameters
    ----------
    subject_id: String
        unique string id of the subject. It should be the same as the one
        used for recording the baseline.
    egg_electrod: Int
        index of the egg electrod that will be used to do the sound
        modulation in the fieldtrip config file.
    egg_freq: Float
        peak frequency of previously selected egg electrod.
    day: String
        Day of the desire resting state mock computation.
    """
    create_mock_soundscapes (subject_id, egg_electrod, egg_freq)


if __name__ == "__main__":
    wrapper_create_mock_soundscape()
