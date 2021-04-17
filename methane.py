"""Estimate B from methane data."""

import matplotlib.pyplot as plt
import pandas as pd
import logging as log
from scipy import signal
from scipy import constants as const
from scipy.stats import linregress
from uncertainties import ufloat as uf
from uncertainties import umath

# Get the datafile we need
filename = 'Methane (sample A) high res'
file = 'data/' + filename + '.csv'

# Laod csv file into pandas objects
data = pd.read_csv(file, names=['Wavelength (nm)', 'Voltage (uV)'])
log.info('Read {} as csv'.format(file))

# Clean up data
data.drop(labels=[0, 1, 2], axis='index', inplace=True)
data = data.astype(float)
data['Wavenumber (cm^-1)'] = 1 / (data['Wavelength (nm)']*(10 ** -7))
data['Energy (J)'] = const.Planck * const.speed_of_light / (data['Wavelength (nm)'] * (10 ** -9))
log.info('Cleaned pandas object ' + filename)

# Get dips
# Inverted data to find dips instead of peaks => absorption
dip_indices = signal.find_peaks(-data['Voltage (uV)'], prominence=10)[0]
dips = data.iloc[dip_indices]

# Split dips into P and R bands
# This also resets the indices so we can use them as quantum number L later
p_band = dips[dips['Wavelength (nm)'] <= 3255].reset_index(drop=True)
r_band = dips[dips['Wavelength (nm)'] >= 3350].reset_index(drop=True)

# Find dv values and average, with error
p_diff = p_band.diff().abs()
r_diff = r_band.diff().abs()
p_mean = p_diff['Wavenumber (cm^-1)'].mean()
p_sem = p_diff['Wavenumber (cm^-1)'].sem()
r_mean = r_diff['Wavenumber (cm^-1)'].mean()
r_sem = r_diff['Wavenumber (cm^-1)'].sem()
p_mean = uf(p_mean, p_sem)
r_mean = uf(r_mean, r_sem)

# Find B from 2B=dv estimate
pb = p_mean / 2
rb = r_mean / 2
b_from_dv = (pb + rb) / 2
print('B estimated from dv in P band: {} cm^-1'.format(pb))
print('B estimated from dv in R band: {} cm^-1'.format(rb))
print('Average B estimate from dv: {} cm^-1'.format(b_from_dv))

# Find linear fits for trendlines
p_trend = linregress(p_band.index, p_band['Energy (J)'])
r_trend = linregress(r_band.index, r_band['Energy (J)'])
# Gradient m = +/-2hcB so ZB = +/- m/(2hc)
rt = abs(uf(r_trend.slope, r_trend.stderr) * (10 ** -2) / (2 * const.Planck * const.speed_of_light))
pt = abs(uf(p_trend.slope, p_trend.stderr) * (10 ** -2) / (- 2 * const.Planck * const.speed_of_light))
b_from_grad = (pt + rt) / 2
print('B estimated from gradient of P band: {} cm^-1'.format(pt))
print('B estimated from gradient of R band: {} cm^-1'.format(rt))
print('Average B estimate from gradient: {} cm^-1'.format(b_from_grad))

# Note conversion of B from cm^-1 to m^-1 by multiplying by 100
B = (b_from_dv + b_from_grad) / 2 * 100
print('Overall B estimate: {} cm^-1'.format(B/100))

# Inertia calculations
I = const.Planck / (8 * const.speed_of_light * B * (const.pi ** 2))
print('Inertia: {} kg m^2'.format(I))

# m_h: mass of oxygen
m_h = 1.008 * const.atomic_mass
r_ch4 = umath.sqrt(3 * I / 8 / m_h) # pylint: disable=no-member
r_co = umath.sqrt(I / (6.857 * const.atomic_mass)) # pylint: disable=no-member
print('Bond length if methane: {} m'.format(r_ch4))
print('Bond length if carbon monoxide: {} m'.format(r_co))

# Plot measured intensities, with dips highlighted.
fig, ax = plt.subplots()
ax.plot(data['Wavelength (nm)'], data['Voltage (uV)'])
ax.scatter(p_band['Wavelength (nm)'], p_band['Voltage (uV)'], color='red')
ax.scatter(r_band['Wavelength (nm)'], r_band['Voltage (uV)'], color='orange')
ax.set_xlabel('Wavelength (nm)')
ax.set_ylabel('Voltage ($\mu$V)') # pylint: disable=anomalous-backslash-in-string
ax.set_title(filename)

# Plot energy against quantum number
fig2, ax2 = plt.subplots()
ax2.scatter(p_band.index, p_band['Energy (J)'], label='P band')
ax2.scatter(r_band.index, r_band['Energy (J)'], label='R band')
plt.plot(p_band.index, p_trend.intercept + p_trend.slope*p_band.index, 'r', label='P trend')
plt.plot(r_band.index, r_trend.intercept + r_trend.slope*r_band.index, 'b', label='R trend')
ax2.set_xlabel('L')
ax2.set_ylabel('Energy (J)') # pylint: disable=anomalous-backslash-in-string
ax2.set_title('Energy vs Quantum Number')
ax2.legend()

# Needed to show plots in terminal environment.
plt.show()