"""Estimate B from methane data."""

import matplotlib.pyplot as plt
import pandas as pd
import logging as log

# Get the datafile we need
filename = 'Methane (sample A) high res.csv'
file = 'data/' + filename

# Laod csv file into pandas objects
data = pd.read_csv(file, names=['Wavelength (nm)', 'Voltage (uV)'])
log.info('Read {} as csv'.format(file))

# Clean up data
data.drop(labels=[0, 1, 2], axis='index', inplace=True)
data = data.astype(float)
log.info('Cleaned pandas object ' + filename)

fig, ax = plt.subplots()
ax.plot(data['Wavelength (nm)'], data['Voltage (uV)'])
ax.set_xlabel('Wavelength (nm)')
ax.set_ylabel('Voltage ($\mu$V)') # pylint: disable=anomalous-backslash-in-string
ax.set_title(filename)

# Needed to show plots in terminal environment.
plt.show()
