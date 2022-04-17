# Copyright (c) 2018 Bart Massey
# [This program is licensed under the "MIT License"]
# Please see the file LICENSE in the source
# distribution of this software for license terms.

# Emit a monophonic square wave on audio output using the
# PyAudio blocking interface.

import sys
import struct
import ctypes
import pyaudio

# Sample rate in frames per second.
SAMPLE_RATE = 48_000

# Frequency in cycles per second.
FREQ = 400

# Output time in milliseconds.
MSECS = 3000


# Size of output buffer in frames. Less than 1024 is not
# recommended, as most audio interfaces will choke
# horribly.
BUFFER_SIZE = 2048

# Total number of frames to be sent.
FRAMES = SAMPLE_RATE * MSECS // 1000

# Total number of buffers to be sent. The audio
# interface requires whole buffers, so this number
# may be one low due to truncation.
BUFFERS = FRAMES // BUFFER_SIZE

# Number of frames constituting a half cycle of the square
# wave at the given frequency. The code only supports
# whole numbers, so the frequency may be slightly higher
# than desired due to truncation.
FRAMES_PER_HALFCYCLE = SAMPLE_RATE // (2 * FREQ)

print("blocking square wave")
print("sample_rate: {}, msecs: {}, freq: {}".format(
        SAMPLE_RATE, MSECS, FREQ))
print("buffer size: {}, buffers: {}, halfcycle: {}".format(
        BUFFER_SIZE, BUFFERS, FRAMES_PER_HALFCYCLE))
print("last buffer nominal size: {}".format(
         BUFFER_SIZE * (BUFFERS + 1) - FRAMES))

# Set up the stream.
pa = pyaudio.PyAudio()
stream = pa.open(rate = SAMPLE_RATE,
                 channels = 1,
                 format = pyaudio.paFloat32,
                 frames_per_buffer = BUFFER_SIZE,
                 output = True)

# State for the square generator.
cycle = 0
sign = 0.05

# Bump the state forward by the given number of frames.
def advance_state(advance):
    global cycle, sign
    cycle += advance
    while cycle >= FRAMES_PER_HALFCYCLE:
        sign = -sign;
        cycle -= FRAMES_PER_HALFCYCLE

# Write all the frames.
written = 0
fbuffer = [0.0] * BUFFER_SIZE
def fill_buffer():
    global fbuffer
    for i in range(BUFFER_SIZE):
        fbuffer[i] = sign
        advance_state(1)

fill_buffer()
fmt = struct.Struct("{}f".format(BUFFER_SIZE))
pbuffer = ctypes.create_string_buffer(4*BUFFER_SIZE)
fmt.pack_into(pbuffer, 0, *fbuffer)
stream.start_stream()
while written < FRAMES:
    # Write buffer.
    try:
        stream.write(pbuffer, exception_on_underflow = True)
    except OSError as status:
        print(status)
        exit(1)

    # Advance to next buffer.
    written += BUFFER_SIZE
    fill_buffer()
    fmt.pack_into(pbuffer, 0, *fbuffer)


# Tear down the stream.
stream.stop_stream()
stream.close()
