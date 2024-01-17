"""
This module contains the `BufferQueue` class which is custom queue in order to
create a sliding buffer for preprocessing of the physiological data.
"""
import numpy as np


class BufferQueue(list):
    """
    Class that implement list but with a maximum length in order to create a
    custom queue
    """

    def __init__(self, max_len, down=None):
        """
        Initialise an instance of BufferQueue

        Parameters
        ----------
        max_len: Int
            Maximum length of the queue.
        down: Int
            Number of point averaged together to create a single datum for
            donwsampling purposes.
        """
        super().__init__()
        self.max_len = max_len
        self.down = down
        self.sub_buffer = []

    def add_data(self, data_sample):
        """
        Add data to the queue and remove older data in order to keep the queue
        length <= max_len
        
        Parameters
        ----------
        data_sample: Array of Float
            Array containing the data to be add to the queue
            
        Returns
        -------
        data_sample: Array of Float
            Array containing the data added to the queue after downsampling
        """
        # Downsampling the incoming data (with previous one) if down has been
        # set
        if self.down:
            down_data_sample = []
            self.sub_buffer = self.sub_buffer + list(data_sample)
            while len(self.sub_buffer) >= self.down:
                down_data_sample.append(np.mean(self.sub_buffer[0 : self.down]))
                del self.sub_buffer[0 : self.down]
            data_sample = down_data_sample

        # Compute how mush data point are exceeding and removing the oldest
        overload = int((len(self) + len(data_sample)) - self.max_len)
        if overload > 0:
            del self[0:overload]

        # Adding the data to the queue
        self += data_sample

        return data_sample

    def prop(self, value):
        """
        Transform a value in a scale where 0 is the minimum of the queue and 1
        is the maximum of the queue
        
        Parameters
        ----------
        value: Float
            Value to be transform in the queue scale
            
        Returns
        -------
        _: Float
            The transformation of the value in the queue scale
        """
        return (value - min(self)) / (max(self) - min(self))

    def full(self):
        """
        Return a boolean ti know if the queue is full
        
        Returns
        -------
        _: Boolean
            True if the queue is full
            False otherwise
        """
        return len(self) == self.max_len
