"""Estimate B from methane data."""

import matplotlib.pyplot as plt
import pandas as pd
import logging as log
from scipy import signal
from uncertainties import ufloat as uf

# Get the datafile we need
filename = 'Methane (sample A) high res.csv'
file = 'data/' + filename

# Laod csv file into pandas objects
data = pd.read_csv(file, names=['Wavelength (nm)', 'Voltage (uV)'])
log.info('Read {} as csv'.format(file))

# Clean up data
data.drop(labels=[0, 1, 2], axis='index', inplace=True)
data = data.astype(float)
data['Wavenumber (cm^-1)'] = 1 / (data['Wavelength (nm)']*(10 ** -7))
log.info('Cleaned pandas object ' + filename)

# Get peaks
peak_indices = signal.find_peaks(data['Voltage (uV)'], prominence=10)[0]
peaks = data.iloc[peak_indices]

# Split peaks into P and R bands
p_band = peaks[peaks['Wavelength (nm)'] <= 3255]
r_band = peaks[peaks['Wavelength (nm)'] >= 3350]

p_diff = p_band.diff().abs()
r_diff = r_band.diff().abs()

p_mean = p_diff['Wavenumber (cm^-1)'].mean()
p_sem = p_diff['Wavenumber (cm^-1)'].sem()
r_mean = r_diff['Wavenumber (cm^-1)'].mean()
r_sem = r_diff['Wavenumber (cm^-1)'].sem()
p_mean = uf(p_mean, p_sem)
r_mean = uf(r_mean, r_sem)

# Find B
pb = p_mean / 2
rb = r_mean / 2
print(pb)
print(rb)

# Plot
fig, ax = plt.subplots()
ax.plot(data['Wavelength (nm)'], data['Voltage (uV)'])
ax.scatter(p_band['Wavelength (nm)'], p_band['Voltage (uV)'], color='red')
ax.scatter(r_band['Wavelength (nm)'], r_band['Voltage (uV)'], color='orange')
ax.set_xlabel('Wavelength (nm)')
ax.set_ylabel('Voltage ($\mu$V)') # pylint: disable=anomalous-backslash-in-string
ax.set_title(filename)

# Needed to show plots in terminal environment.
plt.show()