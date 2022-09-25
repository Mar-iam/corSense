import glob
import numpy as np
import pandas as pd


# Read file named in a specific directory
def read_fnames(p):
    print("Reading Files")
    fnames = sorted(glob.glob(p))

    return fnames


# read rr from a specific file
def read_rr(fn):
    rr = np.loadtxt(fn)

    return rr


# calculate time based on rr file
def get_time(rr):
    t = np.cumsum(rr) / (1000)  # Cumulative sum for all rr intervals; last element is the total duration
    t -= t[0]  # Shift time to zero

    return np.round(t, decimals=2)


def calculate_threshold(xrr, ws):
    alpha = 5.2

    # first and third quartile deviation
    q3 = pd.Series(np.abs(xrr)).rolling(ws, center=True, min_periods=1).quantile(.75)
    q1 = pd.Series(np.abs(xrr)).rolling(ws, center=True, min_periods=1).quantile(.25)

    th = alpha * ((q3 - q1) / 2)

    return th


def detect_outliers(rr, method):
    dRRs = np.diff(rr, prepend=0)
    dRRs[0] = dRRs[1:].median()  # Set first item to a realistic value

    if method == 'fixed':
        dRRs = np.abs(dRRs)

        # calculate the difference between both signals and compare it with 20%
        idx = np.where(dRRs > 0.2 * rr)[0]

        th = rr * 0.2

        mRRs = rr

    elif method == 'median':
        # calculate local median
        medianRR = pd.Series(rr).rolling(11, center=True, min_periods=1).median()

        # calculate difference between RR and local median
        mRRs = rr - medianRR

        # check if mRR greater than predefined constant
        idx = np.where(mRRs > 250)[0]

        th = [250] * len(mRRs)

    elif method == 'adaptive':
        '''
        Algorithm adopted from: 
        Lipponen, J. A., & Tarvainen, M. P. (2019). 
        A robust algorithm for heart rate variability time series artefact correction using novel beat classification. 
        Journal of Medical Engineering and Technology
        '''
        # calculate medianRR  with a window size 10
        medianRR = pd.Series(rr).rolling(11, center=True, min_periods=1).median()

        # EQ4: calculate mRRs
        mRRs = rr - medianRR

        # EQ5: to apply equal threshold for extra and missed beats, mRRs is scaled
        mRRs[mRRs < 0] = 2 * mRRs[mRRs < 0]

        # EQ6: calculate threshold based on mRRs
        ws = 91
        th2 = calculate_threshold(mRRs, ws)

        long = mRRs > th2

        idx = np.where(long == True)[0]

        th = th2

    # Exclude the second value if consecutive
    idx = np.delete(idx, np.where(np.diff(idx) == 1)[0] + 1)

    print(idx)

    return idx, dRRs, mRRs, th


if __name__ == "__main__":
    fname = 'data/sample.txt'

    rr = read_rr(fname)
    detect_outliers(rr, method='fixed')


