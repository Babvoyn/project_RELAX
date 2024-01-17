"""
Module to plot the mock volume modulation of a subject
"""
import json
from datetime import date
from pathlib import Path

import click
import matplotlib.pyplot as plt
from create_mock_soundscapes import SAMP_FREQ


def plot_mod(dict_):
    """
    Function that plot the different mock modulation shuffled

    Parameters
    ----------
    dict_: Dictionary
        dictionary containing the volume modulation
    """
    sub_key = ["or"]
    # sub_key = ["or"]
    for key in ["ecg_", "egg_", "resp_"]:
        #fig, axs = plt.subplots(5, 1, sharex=True)
        for i, sub in enumerate(sub_key):
            plt.plot(
                [x / SAMP_FREQ for x in range(len(dict_[key + sub]))], dict_[key + sub]
            )
        plt.show()



def plot_mock_soundscapes(subject_id):
    """
    Plot mock volume modulation of a given subject
    
    Parameters
    ----------
    subject_id: String
        unique string id of the subject. It should be the same as the one
        used for recording the baseline.
    day: String
        Day of the desire resting state mock computation.
    """
    record_folder = Path(__file__).parent / "../Data/RestingState"
    with open(
        str(record_folder) + f"/RELAX_sub-{subject_id}_PremodulatedSignal.json"
        # f"/RELAX_sub-{subject_id}_PremodulatedSignal.json", "r"
    ) as file:
        data = json.load(file)
    plot_mod(data)


@click.command()
@click.option("--subject_id", prompt="Subject id")
def wrapper_plot_mock_soundscapes(subject_id):
    """
    Wrapper with click interface to plot mock volume modulation of a given subject
    
    Parameters
    ----------
    subject_id: String
        unique string id of the subject. It should be the same as the one
        used for recording the baseline.
    day: String
        Day of the desire resting state mock computation.
    """
    plot_mock_soundscapes(subject_id)


if __name__ == "__main__":
    wrapper_plot_mock_soundscapes()
