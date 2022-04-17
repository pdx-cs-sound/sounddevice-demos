# Copyright (c) 2018 Bart Massey
# [This program is licensed under the "MIT License"]
# Please see the file LICENSE in the source
# distribution of this software for license terms.

# Emit a monophonic square wave on audio output using the
# PyAudio blocking interface.

import sys
import struct
import pyaudio
import time

# Sample rate in frames per second.
SAMPLE_RATE = 48_000

# Frequency in cycles per second.
FREQ = 400

# Output time in seconds.
SECS = 3.0

# Size of output buffer in frames. Less than 1024 is not
# recommended, as most audio interfaces will choke
# horribly.
BUFFER_SIZE = 2048

# Total number of frames to be sent.
FRAMES = SAMPLE_RATE * SECS

# Total number of buffers to be sent. The audio
# interface requires whole buffers, so this number
# may be one low due to truncation.
BUFFERS = FRAMES // BUFFER_SIZE

# Number of frames constituting a half cycle of the square
# wave at the given frequency. The code only supports
# whole numbers, so the frequency may be slightly higher
# than desired due to truncation.
FRAMES_PER_HALFCYCLE = SAMPLE_RATE // (2 * FREQ)

print("non-blocking square wave")
print("sample_rate: {}, secs: {}, freq: {}".format(
        SAMPLE_RATE, SECS, FREQ))
print("buffer size: {}, buffers: {}, halfcycle: {}".format(
        BUFFER_SIZE, BUFFERS, FRAMES_PER_HALFCYCLE))
print("last buffer nominal size: {}".format(
         BUFFER_SIZE * (BUFFERS + 1) - FRAMES))

# Used for the packing thingy.

# State for the square generator.
cycle = 0
sign = 0.8

# Square generator.
def callback(in_data, frames, time_info, status):
    global cycle, sign

    buffer = list()
    for i in range(frames):
        buffer.append(sign)
        cycle += 1
        while cycle >= FRAMES_PER_HALFCYCLE:
            sign = -sign
            cycle -= FRAMES_PER_HALFCYCLE
    return (struct.pack("{}f".format(frames), *buffer), pyaudio.paContinue)

# Set up the stream.
pa = pyaudio.PyAudio()
stream = pa.open(rate = SAMPLE_RATE,
                 channels = 1,
                 format = pyaudio.paFloat32,
                 output = True,
                 frames_per_buffer = BUFFER_SIZE,
                 stream_callback = callback)
            
# Run the stream.
stream.start_stream()
time.sleep(SECS)
stream.stop_stream()
stream.close()
