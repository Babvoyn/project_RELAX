"""
This module contains the `play_wav` function that steam the audio data onto the
soundboard of the computer
"""
import time

import pyaudio


def play_wav(biofeedback):
    """
    Function that seeks the mixed audio data of the block and streams it to the
    soundboard of the computer
    
    Parameters
    ----------
    biofeedback: Biofeedback
        biofeedback instance of the current block
    """
    print("Sound thread started")

    # Get example a wav file in order to get some information
    wf_sample = biofeedback.egg_wavs[0]

    # Creating the stream flux to the soundboard
    py_audio = pyaudio.PyAudio()
    stream = py_audio.open(
        format=py_audio.get_format_from_width(wf_sample.getsampwidth()),
        channels=wf_sample.getnchannels(),
        rate=wf_sample.getframerate(),
        output=True,
    )

    # If we are in a mock block we start the audio immediately otherwise we are
    # waiting for a physiological thread to start it we its buffer is full.
    if biofeedback.cond == "mock":
        biofeedback.audio_on = True
    while not biofeedback.audio_on:
        time.sleep(0.1)

    # Record the audio start time for mock synchronisation
    biofeedback.audio_start = time.time()

    # While the audio is on we get the mixed audio data and send it to the
    # soundboard.
    data = biofeedback.get_mixed_audio_data()
    while biofeedback.audio_on:
        stream.write(data)
        data = biofeedback.get_mixed_audio_data()

    stream.stop_stream()
    stream.close()
    py_audio.terminate()
    print("Sound thread finished")
