import tempfile
import os
from subprocess import call
import matplotlib.pyplot as plt
from f90nml import *
from array import *
import numpy as np
from math import *
import pandas as pd 
import seaborn as sns
from statistics import *
import shutil
import sys
from matplotlib.ticker import FormatStrFormatter

notePath = os.getcwd()

def printFolder():
    for root, dirs, files in os.walk('.'):
        for filename in files:
            print(filename)
        for dirname in dirs:
            print(dirname)
            
def makeDefNamelist():
    nml = {
        'ebm': {
            'seasons' : True,
            'snowball' : False,
            'tend' : 3.154e7, #calculation length (s)
            'dt' : 8.64e4, #time step (s) default = 1 day
            'rot' : 7.27e-5, #earth's present rotation rate
            'a' : 1.49597892E13, #earths orbital semi-major axis (cm)
            'ecc' : 0.0167, #earths orbital eccentricity 
            'peri' : 76.25, #longitude of perihelion wrt vernal equinox (degrees)
            'obl' : 23.5, #earth's obliquity
            'cloudir' : -9.5, #reduction of outgoing infrared by clouds
            'pco20' : 2.84e-4,
            'ocean' : 0.7,
            'igeog' : 1,
            'groundalb' : 0.291,
            'relsolcon' : 1.0,
            'landsnowfrac' : 1.0,
            'fcloud' : 0.50,
            'd0' : 0.58, #initial diffusion coefficient
            'N0' : 1042,
            'rBirth' : 0.027855,
            'rDeath' : 0.0142857,
            'dTpop' : 10,
            'opT' : 290.5,
            'rco2' : 3.459e-4,
            'En' : 1.00,
            'coupled' : True,
            'lverbose' : True,
            'runTime' : 100
        }
    }
    return nml

def newFolder(nml,dirpath): #delete old runfile and make a new one    
    write(nml,'../input.nml',force=True, sort=True) #write the updated namelist
    
    #symlink all relevant files into the temporary directory
    call("ln -s "+notePath+"/driver"+dirpath,shell=True) 
    call("ln -s "+notePath+"/output.dat "+dirpath,shell=True)
    call("ln -s "+notePath+"../input.nml "+dirpath,shell=True)
    
    call("./driver",shell=True) #run the driver
    return dirpath

def deleteFolder():
    #unlink all symbolic links
    call("unlink driver",shell=True)
    call("unlink output.dat",shell=True)
    call("unlink ../input.nml",shell=True)

    os.chdir(os.pardir)    #move one directory up, out of the temporary folder
    
    call("rm -rf tmp*",shell=True) #then remove the temporary folder


def readOutput():
    #instantiate output object
    data = {} #dictionary containing all critical output
    data['time'] = []
    data['temp'] = []
    data['pco2'] = []
    data['pop']  = []
    finalavgtemp=0;
    
    #read in population/avgtemp data
    output = open("output.dat","r")
    next(output) #skip the first line (of headers)
    
    for line in output: #iterates as many years as the program runs
        values = line.split()
        data['time'].append(float(values[0]))
        data['temp'].append(float(values[1]))
        data['pco2'].append(float(values[2]))
        data['pop'].append(float(values[3]))
    
    finalavgtemp=data['temp'][len(data['temp'])-1] # determine the final average temp
    
    output.close() # close output file
    
    df = pd.DataFrame(data)
    
    return df, finalavgtemp