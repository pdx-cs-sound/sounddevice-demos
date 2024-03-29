# Copyright (c) 2018 Bart Massey
# [This program is licensed under the "MIT License"]
# Please see the file LICENSE in the source
# distribution of this software for license terms.

# Emit Shepard Tones on audio output using the
# sounddevice blocking interface.

import math, struct, sys, time
import sounddevice as sd

# Sample rate in frames per second.
SAMPLE_RATE = 48_000

# Size of output buffer in frames.
# Increasing this beyond 2048 is likely to run into this bug
# on PipeWire machines:
# https://gitlab.freedesktop.org/pipewire/pipewire/-/issues/2373
BUFFER_SIZE = 2048

# Number of tones to keep in play.
NTONES = 4

# Interval between tone starts in secs.
TONE_START = 4.0

# Tone sweep time in secs.
TONE_SWEEP = TONE_START * NTONES

# Tone sweep time in samples.
SWEEP_SAMPLES = int(TONE_SWEEP * SAMPLE_RATE)

# Tone start frequency in Hz.
TONE_START_FREQ = 20

# Tone end frequency in Hz.
TONE_END_FREQ = 18000

# Tone max amplitude.
TONE_LOUD = 0.8

# Single sweep generator.
def sweep(i):
    for _ in range(int(TONE_START * i * SAMPLE_RATE)):
        yield 0.0
    while True:
        for t in range(SWEEP_SAMPLES):
            frac = t / SWEEP_SAMPLES
            scale = math.pow(2.0, frac) - 1.0
            f = TONE_START_FREQ + (TONE_END_FREQ - TONE_START_FREQ) * scale
            a = 0.5 * TONE_LOUD * math.sin(math.pi * frac) * scale
            w = 2.0 * math.pi * f * t / SWEEP_SAMPLES
            yield a * math.sin(w)

# Shepard Tone generator.
tones = [sweep(i) for i in range(NTONES)]
def callback(out_data, frames, time_info, status):
    # print(f"callback {frames} {time_info} {status}")
    buffer = list()
    for i in range(frames):
        sample = sum([next(s) for s in tones]) / NTONES
        # print(sample)
        buffer.append(sample)
    out_data[:] = struct.pack("{}f".format(frames), *buffer)

# Set up the stream.
stream = sd.RawOutputStream(
    samplerate = SAMPLE_RATE,
    blocksize = BUFFER_SIZE,
    channels = 1,
    dtype = 'float32',
    callback = callback,
)
            
# Run the stream.
stream.start()
# XXX Awkward wait forever
while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        exit(0)
