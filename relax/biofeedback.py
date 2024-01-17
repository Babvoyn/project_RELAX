"""
This module contains the `Biofeedback` class which is responsible for managing
the biofeedback system. The class connects to the FieldTrip buffer and starts
threads to handle the collection of physiological data, the modulation of the
soundscapes, and the triggering of events.
"""
import json
import os
import time
import wave
from datetime import date
from pathlib import Path
from threading import Thread
from colorama import Fore, Back, Style

import click
import numpy as np
import serial
import itertools

from relax.ecg_feedback import ecg_feedback
from relax.egg_feedback import egg_feedback
from relax.FieldTrip import Client
from relax.play_wav import play_wav
from relax.resp_feedback import resp_feedback

os.chdir("/home/manip3/Desktop/Relax")

def trigger_loop(biofeedback):
    """
    Send trigger to the serial port define in biofeedback as at specific
    interval as well as saving their timestamp inside biofeedback trigger_ts.

    Parameters
    ----------
    biofeedback: Biofeedback
        instance of the current biofeedback
    """
    print("Trigger thread started")
    trigger_delay = [2.5,5,7.5,10,12.5,15]
    n_delay = len(trigger_delay)
    delay_index = 0

    # Start trigger
    biofeedback.serial.write(b"s")
    biofeedback.trigger_ts.append(time.time())
    biofeedback.trigger_name.append("start")
    while biofeedback.recording:
        last = time.time()
        # The function wait to overcome the delay of trigger_delay at the
        # index delay_index modulo the number of delay (cycling).
        while time.time() - last < trigger_delay[delay_index%n_delay] and biofeedback.recording:
            time.sleep(0.1)
        if biofeedback.recording:
            biofeedback.serial.write(b"t")
            biofeedback.trigger_ts.append(time.time())
            biofeedback.trigger_name.append("trigger")
        # Incressing delay_index to change the delay.
        delay_index+=1
    # End trigger
    biofeedback.serial.write(b"e")
    biofeedback.trigger_ts.append(time.time())
    biofeedback.trigger_name.append("end")
    print("Trigger thread finished")


class Biofeedback:
    """
    Manage and link the diffferent function and variable used to do the
    biofeedback.
    """

    def __init__(
        self,
        cond,
        subject_id,
        block,
        egg_pos,
        egg_freq,
        ecg_poses,
        resp_pos,
        sampling_rate,
        hostname,
        port,
        master_volume,
    ):
        """
        Initialise an instance of Biofeedback

        Parameters
        ----------
        condition: String [egg,ecg,resp,mock]
            specify wich biological signal will be modulated online.
        subject_id: String
            unique string id of the subject. It should be the same as the one
            used for recording the baseline.
        block: Int
            block number of the current stimulation.
        egg_pos: Int
            index of the egg electrod that will be used to do the sound
            modulation in the fieldtrip config file.
        egg_freq: Float
            peak frequency of previously selected egg electrod.
        ecg_poses: Array of Int of size 2
            index of the two ecg electrods in the fieldtrip config file.
        resp_pos: Int
            index of the resp belt in the fieldtrip config file.
        sampling_rate: Float
            sampling rate of the fieldtrip buffer (after downsampling)
        hostname: String
            IP address of the fieldtrip buffer
        port: Int
            Port number of the fieldtrip buffer
        """

        # Define constants
        if subject_id == "TRAINING":
            self.SOUNDSCAPE_DURATION = 60
        else :
            self.SOUNDSCAPE_DURATION = 180
        self.SOUNDSCAPE_FADE = 5

        # Set instance variables
        self.cond = cond
        self.subject_id = subject_id
        self.block = block
        self.sampling_rate = sampling_rate
        self.egg_pos = egg_pos
        self.ecg_poses = ecg_poses
        self.resp_pos = resp_pos
        self.egg_freq = egg_freq
        self.master_volume = master_volume
        self.audio_on = False
        self.audio_start = 0
        self.recording = True


        # Define some array that will be put in a json file a the end of the
        # biofeedback
        self.egg_volume = []
        self.resp_volume = []
        self.gr_ts = []
        self.ecg_ts = []
        self.trigger_ts = []
        self.trigger_name = []


        # define the factor associated factor with each sound
        # with in the order : 1. name of the soundscape, 2. ecg, 3. resp, 4. egg factor
        self.factor_array = [
            ["mountain/", 0.48, 0.37, 0.15],
            ["river/",  0.39, 0.32, 0.29],
            ["south/",  0.62, 0.16, 0.22],
                            ]


        # the soundscape order we will play
        self.soundscapes_folder =["river/","mountain/","south/"]

        # Initiate the different threads that will be lauch at the start of the
        # biofeedback
        self.trigger_thread = Thread(target=trigger_loop, args=(self,))
        self.egg_thread = Thread(target=egg_feedback, args=(self,))
        self.resp_thread = Thread(target=resp_feedback, args=(self,))
        self.ecg_thread = Thread(target=ecg_feedback, args=(self,))

        # Load mock modulation data (for testing purposes)
        self.initialise_mock_modulation()

        # Load soundscapes and initialize wave arrays
        self.initialise_wav_array()

        # Set sound modulation
        self.sound_mod = [0.0, 1.0, 0.0]

        # Connect to the FieldTrip buffer
        self.ft_resp = Client()
        self.ft_ecg = Client()
        self.ft_egg = Client()
        self.ft_resp.connect(hostname, port)
        self.ft_ecg.connect(hostname, port)
        self.ft_egg.connect(hostname, port)
        # Initialize headers for biofeedback data
        self.header_resp = self.ft_resp.getHeader()
        self.header_ecg = self.ft_ecg.getHeader()
        self.header_egg = self.ft_egg.getHeader()

        # Check if connection to the FieldTrip buffer was successful
        self.ready = True
        if (
            self.header_resp is None
            or self.header_ecg is None
            or self.header_egg is None
        ):
            print("Connection to FieldTrip buffer failed !")
            self.ready = False
        else:
            print("Connection established with the Fieldtrip buffer")

        # Connect to the serial port
        try:
            self.serial = serial.Serial("/dev/ttyACM0", 115200)
            print("Connection to Serial port established")
        except:
            print("Connection to Serial port failed !")
            self.ready = False
        if self.ready:
            input(Fore.BLACK + Back.GREEN + "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\nMake sure you started the saving on the biosemi device.\nThen press enter to start.\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print(Style.RESET_ALL)
            # Sleepinging time to reach approximatively 45 sc before the sound start for each condition
        if self.cond == "ecg":
            time.sleep(45-2)
        elif self.cond == "resp":
            time.sleep(45-10)
        elif self.cond == "mock":
            time.sleep(45)
            
        self.launch_biofeedback()

    def initialise_mock_modulation(self):
        """
        Initializes mock modulation data if it is available.

        The mock modulation data is used for testing purposes, and consists of
        JSON files containing sound modulation for the EGG, respiratory, and ECG
        soundscapes computed with the resting condition.
        """

        # Finding the right mock-modulation file
        record_folder = "/home/manip3/Desktop/Relax/Data/RestingState/"
        file_list = os.listdir(record_folder)
        expected_file = f"RELAX_sub-{self.subject_id}_PremodulatedSignal.json"

        if expected_file in file_list:
            with open(record_folder+expected_file,"r") as file:
                mock_data = json.load(file)
                # mock_time is the time point for every mock modulation
                # look at create_mock_soundscape to know how it has been created
                self.mock_time = mock_data["time"]
                self.mock_egg = mock_data[f"egg_{int(self.block)}"]
                self.mock_resp = mock_data[f"resp_{int(self.block)}"]
                self.mock_ecg = mock_data[f"ecg_{int(self.block)}"]
        else:
            # If the file is not found, print an error message and exit.
            raise FileNotFoundError(f"{expected_file} was not found.")

    def initialise_wav_array(self):
        """
        Initializes audio files for the soundscapes.
        """
    
        self.root = "/home/manip3/Desktop/Relax/soundscapes"
        
        # Open egg and resp audio files for each soundscape.
        self.egg_wavs = [
            wave.open(str(self.root+"/"+ folder +"/egg.wav"), "rb") for folder in self.soundscapes_folder
        ]
        self.resp_wavs = [
            wave.open(str(self.root+"/"+ folder +"/resp.wav"), "rb") for folder in self.soundscapes_folder
        ]
        # For ecg soundscape we initialize with silence because we you use
        # new wav file when a heart beat is detected.
        self.ecg_wavs = [wave.open(
            str("/home/manip3/Desktop/Relax/tests_sounds/silence.wav"), "rb"
        ),wave.open(
            str("/home/manip3/Desktop/Relax/tests_sounds/silence.wav"), "rb"
        )]
        # In order to minimize the delay between the heart beat and the sound
        # We preload the sound in advance and change wich sound is played by
        # changing the ecg_index.
        self.ecg_index = 0

    def get_sound_volume(self, index):
        """
        This method return the volume of a sound according to its order
        index. This allow to make fade in and fade out transition between the
        different sounds of a layer.

        Parameters
        ----------
        index: Int
            index (and order) of the soundscape accordind to soundscapes_folder

        Returns
        -------
        _: float
            volume of the soundscape at the current time
        """
        # Reformating name
        sc_dur = self.SOUNDSCAPE_DURATION
        fd_dur = self.SOUNDSCAPE_FADE

        # Current time since the start of the sound
        t_point = time.time() - self.audio_start

        # If we are not at the end of the block
        if t_point < (sc_dur * len(self.soundscapes_folder)):
            # Inside the soundscape time limit
            if (
                index * sc_dur + fd_dur <= t_point
                and t_point <= (index + 1) * sc_dur - fd_dur
            ):
                return 1.0
            # Fade out
            if ((index + 1) * sc_dur - fd_dur < t_point and 
                (index + 1) * sc_dur + fd_dur) >= t_point:
                return 1 - ((t_point - ((index + 1) * sc_dur - fd_dur)) / (fd_dur * 2))
            # Fade In
            if index * sc_dur - fd_dur <= t_point and t_point < index * sc_dur + fd_dur:
                return (t_point - (index * sc_dur - fd_dur)) / (fd_dur * 2)
            # Out side the soundscaoe time limit
            return 0.0
        # If the block duration is over we stop the audio and the recording and
        # put the volume to 0
        self.audio_on = False
        self.recording = False
        return 0.0

    def get_layer_data_continuous(self, wav_array,index_type):
        """
        Return the audio data (mixed during transition) of a continuous layer
        i.e. resp or egg at the curent time.
        
        Parameters
        ----------
        wav_array: Array of wav
            Array of wav for a layer in the session order

        index_type: Index of the type of signal : 1 : respiration, 2 : egg

        Returns
        -------
        layer_data: np.array of np.int16 of size 2048
            audio data of the layer at the current time
        """
        layer_data = np.zeros(2048)
        # For every sound of a layer
        for i, wav in enumerate(wav_array):
            volume = self.get_sound_volume(i)
            factor = self.factor_array[i][index_type]
            # If the sound volume isn't null we start reading its wav file
            if volume > 0.0:
                data = np.fromstring(wav.readframes(1024), np.int16) * volume * factor
                # If we reach the end of the wav file we return silence
                # This should not happen has soundscape duration is higher than
                # every wav file duration
                if len(data) < 2048:
                    data = np.zeros(2048)
                # We mix the data
                layer_data += data
        return layer_data

    def get_layer_data_discontinuous(self,wav_array,wav_index):
        """
        Return the audio data (mixed during transition) of a discontinuous layer
        i.e. ecg at the curent time.
        
        Parameters
        ----------
        wav_array: Array of wav
            Array of wav for a layer
        wav_index: Int
            Index of the wav that should be read

        Returns
        -------
        layer_data: np.array of np.int16 of size 2048
            audio data of the layer at the current time
        """
        layer_data = np.fromstring(wav_array[wav_index].readframes(1024), np.int16)*self.factor_array[wav_index][1]
        # If we reach the end of the wav file we return silence
        if len(layer_data) < 2048:
            layer_data = np.zeros(2048)
        return layer_data

    def get_mixed_audio_data(self):
        """
        Return the mixed audio data of the differents layers
        i.e. ecg, egg and resp at the curent time. Also, record the volume of
        the egg and resp layers for offline check.

        Returns
        -------
        audio_data: np.array of np.int16 of size 2048
            audio data of the soundscape at the current time
        """

        # Get the audio data of every layer
        ecg_data = self.get_layer_data_discontinuous(self.ecg_wavs,self.ecg_index)
        egg_data = self.get_layer_data_continuous(self.egg_wavs,3)
        resp_data = self.get_layer_data_continuous(self.resp_wavs,2)

        # Mixing the audio data
        audio_data = ((
            (egg_data * (0.2 + 0.8 * self.sound_mod[0]))
            + (ecg_data * self.sound_mod[1])
            + (resp_data * (0.2 + 0.8 * self.sound_mod[2]))
        )*self.master_volume).astype(np.int16)

        # Recording the volume of the continuous layers and their timestamps
        self.egg_volume.append(self.sound_mod[0])
        self.resp_volume.append(self.sound_mod[2])
        self.gr_ts.append(time.time())

        return audio_data.tostring()

    def save(self):
        """
        Save the different information of the biofeedback block.
        """
        date_string = str(date.today())
        # Save the different variable inside a dictionary
        dict_ = {
            "subject_id" : self.subject_id,
            "date" : date_string,
            "condition" : self.cond,
            "block": self.block,
            "egg_pos": self.egg_pos,
            "egg_freq": self.egg_freq,
            "soudscapes_order": self.soundscapes_folder,
            "trigger_ts": list(np.array(self.trigger_ts, dtype=np.float)),
            "trigger_name" : list(np.array(self.trigger_name, dtype=str)),
            "ecg_ts": list(np.array(self.ecg_ts, dtype=np.float)),
            "resp_volume": list(np.array(self.resp_volume, dtype=np.float)),
            "egg_volume": list(np.array(self.egg_volume, dtype=np.float)),
            "gr_ts": list(np.array(self.gr_ts, dtype=np.float)),
            
        }

        # Get the right file name and folder

        file = ("/home/manip3/Desktop/Relax"+f"/Data/Biofeedback/RELAX_sub-{self.subject_id}_ses-{self.block}_cond-{self.cond}_Biofeedback.json")

        # Save the dictionary as a json file
        if not os.path.exists("Data/Biofeedback"):
            os.mkdir("Data/Biofeedback")
        with open(str(file),"w") as open_file:
            json.dump(dict_, open_file)
        print("File saved")
        print("-------------------------------------------\n\n")
        print("End of the biofeedback")
        print("\n\n-------------------------------------------")

    def launch_biofeedback(self):
        """
        Function run after the biofeedback instance have been initialize and
        lauch the different threads used to make the biofeedback works.
        """
        self.trigger_thread.start()
        self.ecg_thread.start()
        self.resp_thread.start()
        self.egg_thread.start()
        # Function run on the main thread
        play_wav(self)

        self .trigger_thread.join()
        # Save the information at the and of the block

        if self.subject_id == "TRAINING":
            print("-------------------------------------------\n\n")
            print("End of relaxation")
            print("\n\n-------------------------------------------")
        else: 
            self.save()

        #### ADDED TO CLOSE PORT SERIE

        self.serial.close()

"""
    Function to run a biofeedback block using normal input
"""

@click.command()
@click.option(
    "--cond",
    prompt="Condition",
    type=click.Choice(["egg", "ecg", "resp", "mock"], case_sensitive=False),
)
@click.option("--subject_id", prompt="Subject id")
@click.option("--block", type=int, prompt="Block")
@click.option("--egg_pos", type=int, prompt="Egg pos")
@click.option("--egg_freq", type=float, prompt="Egg peak frequency")
@click.option("--ecg_poses", type=list, prompt="Ecg poss", default=[2, 8])
@click.option("--resp_pos", type=int, prompt="Resp pos", default=0)
@click.option("--sampling_rate", type=int, prompt="Sampling rate", default=2048)
@click.option("--hostname", type=str, prompt="Fieldtrip ip", default="192.168.1.1")
@click.option("--port", type=int, prompt="Fieldtrip port", default=1972)
@click.option("--master_volulme", type=int, prompt="master_volulme", default=0.025)
def start_biofeedback(
    cond,
    subject_id,
    block,
    egg_pos,
    egg_freq,
    ecg_poses,
    resp_pos,
    sampling_rate,
    hostname,
    port,
    master_volulme
    ):
    
    """
    Function to run a biofeedback block using the GUI of the click library.
    """
    Biofeedback(
        cond,
        subject_id,
        block,
        egg_pos,
        egg_freq,
        ecg_poses,
        resp_pos,
        sampling_rate,
        hostname,
        port,
        master_volulme
    )


if __name__ == "__main__":
    print('Launch from main')
    start_biofeedback()
else :
    print('Import biofeedback')
