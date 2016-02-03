# -*- coding: utf-8 -*-
"""
Created on Mon Feb 01 20:49:48 2016
@author: Devin
"""
import sys
if ~(r'F:\Documents\Yale\Junior Year\HFSSpython\pyHFSS' in sys.path):
    sys.path.append(r'F:\Documents\Yale\Junior Year\HFSSpython\pyHFSS')
import hfss, numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import pandas as pd

class simulated_wg(object):
    def __init__(self):
        prefix = "../data/parameters"
        name = prefix + "capacitance" + ".npy"
        self.capacitance = np.load(name)
        name = prefix + "voltage" + ".npy"
        self.voltage = np.load(name)
        name = prefix + "inductance" + ".npy"
        self.inductance = np.load(name)
        name = prefix + "current" + ".npy"
        self.current = np.load(name)
        name = "../data/parametersangles.npy"
        self.angles = np.load(name)
        name = "../data/parameterseigenmodes.npy"
        self.eigenmodes = np.load(name)
    
    def build_L_mat(self):
        smooth_l = interpolate_outliers(self.angles, self.inductance)        
        size = len(smooth_l)
        self.L = np.zeros((size,size))
        d_l = 1#5.89*.001*2*np.pi/100
        for i in range(size):
            self.L[i][i] += (d_l*smooth_l[i])**-1
            self.L[(i+1)%size][i] += -(d_l*smooth_l[i])**-1
            self.L[i][(i+1)%size] += -(d_l*smooth_l[i])**-1
            self.L[(i+1)%size][(i+1)%size] += (d_l*smooth_l[i])**-1

    def build_C_mat(self):
        smooth_c = interpolate_outliers(self.angles, self.capacitance)
        size = len(smooth_c)
        self.C = np.zeros((size,size))
        d_l = 1#5.89*.001*2*np.pi/100
        for i in range(size):
            self.C[i][i] += (d_l*smooth_c[i])
            self.C[(i+1)%size][i] += -(d_l*smooth_c[i])
            self.C[i][(i+1)%size] += -(d_l*smooth_c[i])
            self.C[(i+1)%size][(i+1)%size] += (d_l*smooth_c[i])

    def test_interpolate(self,plot_me = True):
        potted = self.inductance
        voltage = interpolate_outliers(self.angles,potted, plot_me = plot_me)
        plt.plot(self.angles,voltage, self.angles, potted)
        ax = plt.gca()
        ax.set_ylim(min(voltage), max(voltage))
        plt.show()
        
    def get_frequencies(self):
        LC = np.dot(np.linalg.inv(self.C),self.L)
        print LC
        self.evals = np.linalg.eigvals(LC)
        print np.sqrt(self.evals)

def interpolate_outliers(angle, data, threshold=1., window = 5, plot_me = False):
    '''
    Function to smooth outliers from the data set. Applys moving
    average smoothing and cyclic boundary conditions. Threshold
    is set by:
    threshold - number of standard deviations from average which defines outliers
    window - number of points in each direction used for average
    '''
    df = pd.DataFrame({'parameter':data},index=angle)
    #mean_data = np.mean(df['parameter'])
    df['data_mean'] = pd.rolling_median(df['parameter'].copy(), window=window, center=True).fillna(method='bfill').fillna(method='ffill')
    difference = np.abs(df['parameter'] - df['data_mean'])#mean_data)#
    outlier_idx = difference > threshold*df['parameter'].std()    
    
    s = df['parameter'].copy()
    s[outlier_idx] = np.nan
    s.interpolate(method='spline', order=1, inplace=True)
    df['cleaned_parameter'] = s
    
    if (plot_me == True):
        figsize = (7, 2.75)
        fig, ax = plt.subplots(figsize=figsize)
        df['parameter'].plot()
        df['cleaned_parameter'].plot()
        ax.set_ylim(min(df['cleaned_parameter']), max(df['cleaned_parameter']))
    return np.array(df['cleaned_parameter'])


        
def main():
    sim_wg = simulated_wg()
    sim_wg.test_interpolate()
    #sim_wg.build_L_mat()
    #sim_wg.build_C_mat()
    #sim_wg.get_frequencies()
    
    
if __name__ == "__main__":
    main()            