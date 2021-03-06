#!/usr/bin/env python
#coding: utf-8

""" This work is licensed under a Creative Commons Attribution 3.0 Unported License.
	Frank Zalkow, 2012-2013 """

import numpy as np
from matplotlib import pyplot as plt
import scipy.io.wavfile as wav
from numpy.lib import stride_tricks
import matplotlib.pyplot as plt
from scipy import signal

""" short time fourier transform of audio signal """
def stft(sig, frameSize, overlapFac=0.5, window=np.hanning):
	win = window(frameSize)
	hopSize = int(frameSize - np.floor(overlapFac * frameSize))

	# zeros at beginning (thus center of 1st window should be for sample nr. 0)
	samples = np.append(np.zeros(int(np.floor(frameSize/2.0))), sig)    
	# cols for windowing
	cols = np.ceil( (len(samples) - frameSize) / float(hopSize)) + 1
	# zeros at end (thus samples can be fully covered by frames)
	samples = np.append(samples, np.zeros(frameSize))

	frames = stride_tricks.as_strided(samples, shape=(int(cols), frameSize), strides=(samples.strides[0]*hopSize, samples.strides[0])).copy()
	frames *= win
	
	return np.fft.rfft(frames)    
	
""" scale frequency axis logarithmically """    
def logscale_spec(spec, sr=44100, factor=20.):
	timebins, freqbins = np.shape(spec)

	scale = np.linspace(0, 1, freqbins) ** factor
	scale *= (freqbins-1)/max(scale)
	scale = np.unique(np.round(scale))
	
	# create spectrogram with new freq bins
	newspec = np.complex128(np.zeros([timebins, len(scale)]))
	for i in range(0, len(scale)):
		if i == len(scale)-1:
			newspec[:,i] = np.sum(spec[:,int(scale[i]):], axis=1)
		else:        
			newspec[:,i] = np.sum(spec[:,int(scale[i]):int(scale[i+1])], axis=1)
	
	# list center freq of bins
	allfreqs = np.abs(np.fft.fftfreq(freqbins*2, 1./sr)[:freqbins+1])
	freqs = []
	for i in range(0, len(scale)):
		if i == len(scale)-1:
			freqs += [np.mean(allfreqs[int(scale[i]):])]
		else:
			freqs += [np.mean(allfreqs[int(scale[i]):int(scale[i+1])])]
	
	return newspec, freqs

""" plot spectrogram"""
def plotstft(audiopath, binsize=2**10, plotpath=None, colormap="jet"):
	samplerate, samples = wav.read(audiopath)
	s = stft(samples, binsize)
	
	sshow, freq = logscale_spec(s, factor=1.0, sr=samplerate)
	ims = 20.*np.log10(np.abs(sshow)/10e-6) # amplitude to decibel
	
	timebins, freqbins = np.shape(ims)
	
	plt.figure(figsize=(15, 7.5))
	plt.imshow(np.transpose(ims), origin="lower", aspect="auto", cmap=colormap, interpolation="none")
	plt.colorbar()

	plt.xlabel("time (s)")
	plt.ylabel("frequency (hz)")
	plt.xlim([0, timebins-1])
	plt.ylim([0, freqbins])

	xlocs = np.float32(np.linspace(0, timebins-1, 5))
	plt.xticks(xlocs, ["%.02f" % l for l in ((xlocs*len(samples)/timebins)+(0.5*binsize))/samplerate])
	ylocs = np.int16(np.round(np.linspace(0, freqbins-1, 10)))
	plt.yticks(ylocs, ["%.02f" % freq[i] for i in ylocs])
	
	if plotpath:
		plt.savefig(plotpath, bbox_inches="tight")
	else:
		plt.show()
		
	plt.clf()

audio_file_name = "audio_-0SdAVK79lg"
audio_file_path = audio_file_name + ".wav"
# plotstft(audio_file_path,plotpath=audio_file_name+"_spectogram.png")


# Alternative Method
sample_rate, samples = wav.read(audio_file_path)
# It should be nperseg = 480 and overlap = 240 ? But I get 241 x 199
# Below values give 257 x 200

time = 0.5
start = int(time*48000)-24000
end   = int(time*48000)+24000

frequencies, times, spectrogram = signal.spectrogram(samples[start:end], sample_rate, nperseg=512, noverlap=274)
print(spectrogram.shape)
plt.figure()
plt.pcolormesh(times, frequencies, spectrogram)
plt.imshow(np.log(spectrogram))
print(spectrogram.shape)
plt.ylabel('Frequency [Hz]')
plt.xlabel('Time [5 msec]')
	# plt.savefig('spectro_0')
plt.show()