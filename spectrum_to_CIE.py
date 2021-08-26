# coding: utf-8
import glob
import os.path
import re

import colour
import matplotlib.pyplot as plt
import pandas as pd
from colour.plotting import *
from scipy.signal import savgol_filter

files = glob.glob('*.txt')
files.sort(key=os.path.getmtime)

plot_chromaticity_diagram_CIE1931(standalone=False)

for spectrum in files:

    newf = ""
    with open(spectrum, 'r') as f:
        for line in f:
            if not any(c.isalpha() for c in line):
                if line.find('+'):
                    newf += line
        f.close()
    with open(spectrum, 'w') as f:
        f.write(newf)
        f.close()

    data = pd.read_csv(spectrum, delim_whitespace=True, index_col=False)
    data.columns = ['a', 'b']
    df = pd.DataFrame(data)
    df.b = savgol_filter(df.b, 23, 3) - 360
    df.to_csv(spectrum + '_processed', header=False, index=False, sep='\t', mode='w')

    dictionary = {}

    with open(spectrum + '_processed', 'r') as f:
        for line in f:
            a = re.findall(r'[-+]?\d*\.\d+|\d+', line)
            dictionary.update({a[0]: a[1]})

    sd = colour.SpectralDistribution(dictionary, name='Sample')
    cmfs = colour.STANDARD_OBSERVERS_CMFS['CIE 1931 2 Degree Standard Observer']
    illuminant = colour.ILLUMINANTS_SDS['A']
    sd_copy = sd.copy()
    sd_copy.interpolate(colour.SpectralShape(410, 700, 1))
    x, y = colour.XYZ_to_xy(colour.sd_to_XYZ(sd_copy, cmfs) / 100)
    print(x, y)
    plt.plot(x, y, 'x', color='black')

plt.savefig('CIE_with_color_coordinates', dpi=400)
render(standalone=True)
