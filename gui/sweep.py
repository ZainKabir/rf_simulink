import numpy as np
from scipy import signal

class Simulator(object):

    """Simulates multiple sweeps and extracts movement. """

    def __init__(self, sfreqs, sintens, noise=25, samples=500):
        """Initialize parameters.
        
        Params
        ------
        sfreqs : float array
            Delta frequencies of static objects.

        sintens : float array
            Intensities of static objects.

        noise: int
            Intensity of simulated noise

        samples: int
            Samples in a single sweep

        Attributes
        ----------
        static: array
            Signal generated by static objects frequencies

        basebands: 2-d array
            TOF profile for each sweep.
        
        ffts: 2-d array
            FFT of TOF profiles of each sweep.
        """

        self.sfreqs = sfreqs
        self.sintens = sintens
        self.noise = noise
        self.samples = samples
        self._set_static()

    def set_params(self, vfreqs, vintens, extract=False):
        """Set moving object frequencies on runtime."""

        self.vfreqs = vfreqs
        self.vintens = vintens

        if extract:
            self.extract_movement()
            return self.diffs, self.find_tofs

    def _set_static(self):
        """Helper method to generate static signal."""

        x = np.linspace(-np.pi, np.pi, self.samples)
        self.static = np.zeros(self.samples)
        
        for i,f in zip(self.sintens, self.sfreqs):
            self.static += i*np.sin(f*x)
        
        noise = np.random.normal(0, 1, self.samples)
        self.static += 25 * noise

    def simulate_mixer(self):
        """Generate TOF profile for each sweep."""

        x = np.linspace(-np.pi, np.pi, self.samples)
        self.basebands = [self.static + (self.vintens * np.sin(f*x)) for f in self.vfreqs]  
        return self.basebands
    
    def _add_diffs(self):
        """Add diffs of ffts of TOF profiles."""
        ffts = [np.abs(np.fft.rfft(b)) for b in self.basebands]
        self.diffs = np.zeros(len(ffts[0]))

        for i in range(0, len(ffts) - 1):
            self.diffs += np.abs(ffts[i+1] - ffts[i])
        
        return self.diffs

    def find_tofs(self, threshold):
        """From fft diffs, find samples that exceed a threshold"""
        return self.diffs[self.diffs > threshold]
       
    def extract_movement(self):
        """Extract object movement."""
        self.simulate_mixer()
        return self._add_diffs()

    def extract_tofs(self):
        """Extract tofs."""
        self.simulate_mixer()
        self._add_diffs()
        return self.find_tofs

