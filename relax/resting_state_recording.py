"""
Module to record resting state
"""
from datetime import date
from pathlib import Path
from time import time

import json
import click
import mne
import numpy as np
import os
import serial

from relax.FieldTrip import Client

CH_NAMES = [
    "Resp",
    "EGG1",
    "EGG2",
    "EGG3",
    "EGG4",
    "EGG5",
    "EGG6",
    "EGG7",
    "EGG8",
    "Sound",
    "GSR1",
    "GSR2",
    "VEOG1",
    "VEOG2",
    "EMGf1",
    "EMGf2",
    "EMGt1",
    "EMGt2",
    "AF3",
    "AF4",
    "P3",
    "P4",
    "Fpz",
    "Cz",
]
CH_TYPES = ["eeg" for _ in range(len(CH_NAMES))]

trigger_ts = []


def save_json(subject_id,trigger_ts):
        """
        Save the different information of the biofeedback block.
        """
        # Save the different variable inside a dictionary
        dict_ = {
            "subject_id" : subject_id,
            "trigger_ts": list(np.array(trigger_ts, dtype=np.float)),
        }

        # Get the right file name and folder

        file = ("/home/manip3/Desktop/Relax"+f"/Data/RestingState/RELAX_sub-{subject_id}_RestingStateTrigger.json")

        # Save the dictionary as a json file
        if not os.path.exists("Data/RestingState"):
            os.mkdir("Data/RestingState")
        with open(str(file),"w") as open_file:
            json.dump(dict_, open_file)
        print("File saved")
        print("-------------------------------------------\n\n")
        print("End of the biofeedback")
        print("\n\n-------------------------------------------")



def start_recording(subject_id, duration, sampling_rate, hostname, port):
    """
    Start the recording of the resting state.
    
    Parameters
    ----------
    subject_id: String
        unique string id of the subject. It should be the same as the one
        used for recording the baseline.
    duration: Int
        Duration in second of the recording
    sampling_rate: Float
        sampling rate of the fieldtrip buffer (after downsampling)
    hostname: String
        IP address of the fieldtrip buffer
    port: Int
        Port number of the fieldtrip buffer
    """
    ##### ADDED FOR SYNCH ####
    try:
        serial_trigger = serial.Serial("/dev/ttyACM0", 115200)
        print("Connection to Serial port established")
    except:
        BufferError("Connection to Serial port failed !")

    ft_client = Client()
    ft_client.connect(hostname, port)
    ft_header = ft_client.getHeader()
    if ft_header is None:
        print("Connection to FieldTrip buffer failed !")
    else:
        print("Connection established with the Fieldtrip buffer")
        record_folder = str(Path(__file__).parent / "../Data/RestingState")
        expected_file =record_folder+f"RELAX_sub-{subject_id}_RestingState.fif"
        check_file = os.path.isfile(expected_file)
        if check_file:
            raise ValueError("This file already exist !")
        data = [[] for n in range(ft_header.nChannels)]
        old_smp, old_evt = ft_client.wait(ft_header.nSamples, ft_header.nEvents, 500)
        start = time()
        serial_trigger.write(b"s")
        trigger_ts.append(time())

        while time() - start <= duration:
            new_smp, new_evt = ft_client.wait(old_smp, old_evt, 500)
            if new_smp == old_smp:
                continue
            data_sample = np.array(ft_client.getData([old_smp, new_smp - 1])).T
            for i, sub_data in enumerate(data_sample):
                data[i] += list(sub_data)
            old_smp = new_smp
            old_evt = new_evt
        serial_trigger.write(b"e")
        trigger_ts.append(time())
        print("Record completed")
        print("Conversion to fif file")
        info = mne.create_info(CH_NAMES, sfreq=sampling_rate, ch_types=CH_TYPES)
        raw  = mne.io.RawArray(data, info)
        file = str(
            Path(__file__).parent / f"../Data/RestingState/RELAX_sub-{subject_id}_RestingState.fif"
        )
        raw.save(file, overwrite=True)
        save_json(subject_id,trigger_ts)
        serial_trigger.close()


@click.command()
@click.option("--subject_id", type=str, prompt="Subject id")
@click.option("--duration", type=int, prompt="Duration (s)",default = 700)
@click.option("--sampling_rate", type=int, prompt="Sampling rate", default=2048)
@click.option("--hostname", type=str, prompt="Fieldtrip ip", default="192.168.1.1")
@click.option("--port", type=int, prompt="Fieldtrip port", default=1972)
def wrapper_start_recording(subject_id, duration, sampling_rate, hostname, port):
    """
    Wrapper to start the recording of the resting state.
    
    Parameters
    ----------
    subject_id: String
        unique string id of the subject. It should be the same as the one
        used for recording the baseline.
    duration: Int
        Duration in second of the recording
    sampling_rate: Float
        sampling rate of the fieldtrip buffer (after downsampling)
    hostname: String
        IP address of the fieldtrip buffer
    port: Int
        Port number of the fieldtrip buffer
    """
    start_recording(subject_id, duration, sampling_rate, hostname, port)


if __name__ == "__main__":
    wrapper_start_recording()
