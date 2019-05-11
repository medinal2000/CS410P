import wave
from scipy.io.wavfile import read
import numpy
import sys
import math


def goertzel_filter(samples, target_frequency):
    sample_rate = 48000
    num_samples = len(samples)
    w0 = (2 * math.pi * target_frequency)/sample_rate

    norm = numpy.exp(1j * w0 * num_samples)
    coefficients = numpy.array([-1j * w0 * k for k in range(num_samples)])
    coefficients /= numpy.max(numpy.abs(coefficients), axis=0)

    y = numpy.abs(norm * numpy.dot(coefficients, samples))
    
    return y


# read in audio file
file_name = "lamkin.wav"#sys.argv[1]
audio_file = read(file_name)
samples = numpy.array(audio_file[1], dtype=float)


# get raw bit stream
samples_per_chunk = 160
i = 0
k = samples_per_chunk - 1
index = 0
bit_stream = numpy.empty(int(len(samples)/160), dtype='i1')

while i < len(samples):
    mark = goertzel_filter(samples[i:k], 2225)
    space = goertzel_filter(samples[i:k], 2025)
        
    if mark > space:
        bit_stream[index] = 1
    else:
        bit_stream[index] = 0
      
    index += 1
    i += samples_per_chunk
    k += samples_per_chunk
    

#process raw bit stream to get the good bit stream by
#removing stop/space characters and changing endianess
num_chunks = int(len(samples)/(160*10))
    
split_array = numpy.array_split(bit_stream, num_chunks)
good_bit_stream = numpy.empty((num_chunks, 8), dtype='i1')

for i in range(num_chunks):
    flipped = numpy.flip(split_array[i])
    good_bit_stream[i] = flipped[1:9]


# change byte streams into the message
binary_values = [128, 64, 32, 16, 8, 4, 2, 1]
message = ""

for i in range(num_chunks):
    number = int(numpy.dot(good_bit_stream[i], binary_values))
    character = chr(number)
    message = message + str(character)

print(message)