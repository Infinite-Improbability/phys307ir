"""Plot graphs of intensity against wavenumber for selected datasets."""

import matplotlib.pyplot as plt
import pandas as pd
from os import listdir
import logging as log

# Look for all data files. This also returns subfolders.
files = listdir('data')
log.info('Found {} files and subdirectories: {}'.format(len(files), files))

# Laod csv files into pandas objects
datasets = {}
for filename in files:
    if '.csv' not in filename:
        log.info('Skipped csv read for ' + filename)
        continue
    path = 'data/' + filename
    datasets[filename.replace('.csv', '')] = pd.read_csv(
        path, names=['Wavelength (nm)', 'Voltage (uV)'])
    log.info('Read {} as csv'.format(path))

# Clean up data
for key, data in datasets.items():
    data.drop(labels=[0, 1, 2], axis='index', inplace=True)
    data = data.astype(float)
    data['Wavenumber (cm^-1)'] = 1 / (data['Wavelength (nm)']*(10 ** -7))
    datasets[key] = data
    log.info('Cleaned pandas object ' + key)

for key, data in datasets.items():
    fig, ax = plt.subplots()
    ax.plot(data['Wavenumber (cm^-1)'], data['Voltage (uV)'])
    ax.set_xlabel('Wavenumber (cm^-1)')
    ax.set_ylabel('Voltage ($\mu$V)') # pylint: disable=anomalous-backslash-in-string
    ax.set_title(key)

# Needed to show plots in terminal environment.
plt.show()
