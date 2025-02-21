# region problem statement
'''
	(50 pts) Create a Python program that simulates an industrial-scale gravel production process where crushed rocks
	are sieved through a pair of screens:  the first screen is a large aperture screen that excludes rocks above a
	certain size and the second screen has a smaller aperture.  The product is the fraction of rocks from between the screens.

Assumptions:
	While the actual gavel is not spherical, we will assume that the rocks are spherical.
	Prior to sieving, the gravel follows a log-normal distribution (i.e., loge(D) is N(μ,σ)), where D is the rock
	diameter, μ=mean of ln(D) and σ= standard deviation of ln(D).  After sieving, the log-normal distribution is now
	truncated to have a maximum (Dmax) and minimum size (Dmin) imposed by the aperture size of the screens.

Your program should solicit input from the user (with suggested default values) μ, σ, Dmax and Dmin.  It should then
produce 11 samples of N=100 rocks randomly selected from the truncated log-normal distribution and report to the user
through the cli the sample mean (D̅) and variance (S2) of each sample as well as the mean and variance of the sampling mean.

Note:
The standard log-normal probability density function (PDF) is normalized over (0,∞) by:
f(D)=1/(Dσ√(2π))*exp(-((ln(D)-μ)^2/(2σ^2))); ∫₀∞f(D)dD=1

And the normalized truncated log-normal PDF is given by:
f_trunc(D)=f(D)/(F(Dmax)-F(Dmin))

Your grade will be based on your efficient use of imports of the allowed modules, use of functions and function calls,
use of lists and list comprehensions, your clarity in your docstrings and comments and your overall approach to the
problem.  Clearly state your assumptions in the docstring of the main function.
'''
# endregion

# region imports
import math
from random import random as rnd
from scipy.integrate import quad
from scipy.optimize import fsolve
from copy import deepcopy as dc
from matplotlib import pyplot as plt
import numpy as np


# endregion

# region functions
def ln_PDF(args):
    '''
    Computes f(D) for the log-normal probability density function.
    :param args: (D, mu, sigma)
    :return: f(D)
    '''
    D, mu, sig = args  # unpack the arguments
    if D == 0.0:
        return 0.0
    p = 1 / (D * sig * math.sqrt(2 * math.pi))
    _exp = -((math.log(D) - mu) ** 2) / (2 * sig ** 2)
    return p * math.exp(_exp)


def tln_PDF(args):
    """
    Compute the value of the truncated log-normal probability density function.
    :param args: tuple (D, mu, sig, F_DMin, F_DMax)
    :return: f_trunc(D)
    """
    D, mu, sig, F_DMin, F_DMax = args
    return ln_PDF((D, mu, sig)) / (F_DMax - F_DMin)


def F_tlnpdf(args):
    '''
    Integrates the truncated log-normal probability density function from D_Min to D and returns the probability.
    :param args: tuple (mu, sig, D_Min, D_Max, D, F_DMax, F_DMin)
    :return: cumulative probability from D_Min to D
    '''
    mu, sig, D_Min, D_Max, D, F_DMax, F_DMin = args
    if D > D_Max or D < D_Min:
        return 0
    # Use quad integration for the truncated PDF
    result, err = quad(lambda x: tln_PDF((x, mu, sig, F_DMin, F_DMax)), D_Min, D)
    return result


def makeSample(args, N=100):
    """
    Uses the truncated log-normal probability density function to compute D for each of the N random probabilities.
    :param args: tuple (ln_Mean, ln_sig, D_Min, D_Max, F_DMax, F_DMin)
    :param N: number of items in the sample
    :return: d_s a list of rock sizes
    """
    ln_Mean, ln_sig, D_Min, D_Max, F_DMax, F_DMin = args  # unpack args
    # Generate uniformly distributed probability values
    probs = [rnd() for _ in range(N)]
    # Use fsolve to find D such that the cumulative probability equals the generated probability
    d_s = [fsolve(lambda x: F_tlnpdf((ln_Mean, ln_sig, D_Min, D_Max, x, F_DMax, F_DMin)) - probs[i],
                  (D_Min + D_Max) / 2)[0] for i in range(len(probs))]
    return d_s


def sampleStats(D, doPrint=False):
    """
    Computes the mean and variance of the values in D.
    :param D: list of values
    :param doPrint: bool, print feedback if True
    :return: (mean, variance)
    """
    N = len(D)
    mean = sum(D) / N
    var = sum((d - mean) ** 2 for d in D) / (N - 1)
    if doPrint:
        print(f"mean = {mean:0.3f}, var = {var:0.3f}")
    return (mean, var)


def getPreSievedParameters(args):
    """
    Prompts the user to input the mean and standard deviation for the log-normal probability density function.
    :param args: default values (mean_ln, sig_ln)
    :return: (mean_ln, sig_ln)
    """
    mean_ln, sig_ln = args
    st_mean_ln = input(
        f'Mean of ln(D) for the pre-sieved rocks? (ln({math.exp(mean_ln):0.1f})={mean_ln:0.3f}, where D is in inches):').strip()
    mean_ln = mean_ln if st_mean_ln == '' else float(st_mean_ln)
    st_sig_ln = input(f'Standard deviation of ln(D) for the pre-sieved rocks? ({sig_ln:0.3f}):').strip()
    sig_ln = sig_ln if st_sig_ln == '' else float(st_sig_ln)
    return (mean_ln, sig_ln)


def getSieveParameters(args):
    """
    Prompts the user for the sieve parameters.
    :param args: (D_Min, D_Max)
    :return: (D_Min, D_Max)
    """
    D_Min, D_Max = args
    st_D_Max = input(f'Large aperture size? ({D_Max:0.3f})').strip()
    D_Max = D_Max if st_D_Max == '' else float(st_D_Max)
    st_D_Min = input(f'Small aperture size? ({D_Min:0.3f})').strip()
    D_Min = D_Min if st_D_Min == '' else float(st_D_Min)
    return (D_Min, D_Max)


def getSampleParameters(args):
    """
    Prompts the user for sample parameters.
    :param args: (N_samples, N_SampleSize)
    :return: (N_samples, N_SampleSize)
    """
    N_samples, N_sampleSize = args
    st_N_Samples = input(f'How many samples? ({N_samples})').strip()
    N_samples = N_samples if st_N_Samples == '' else int(st_N_Samples)
    st_N_SampleSize = input(f'How many items in each sample? ({N_sampleSize})').strip()
    N_sampleSize = N_sampleSize if st_N_SampleSize == '' else int(st_N_SampleSize)
    return (N_samples, N_sampleSize)


def getFDMaxFDMin(args):
    """
    Computes F_DMax and F_DMin using the log-normal distribution.
    :param args: (mean_ln, sig_ln, D_Min, D_Max)
    :return: (F_DMin, F_DMax)
    """
    mean_ln, sig_ln, D_Min, D_Max = args
    F_DMax, err = quad(lambda x: ln_PDF((x, mean_ln, sig_ln)), 0, D_Max)
    F_DMin, err = quad(lambda x: ln_PDF((x, mean_ln, sig_ln)), 0, D_Min)
    return (F_DMin, F_DMax)


def makeSamples(args):
    """
    Makes samples and computes the sample means.
    :param args: (mean_ln, sig_ln, D_Min, D_Max, F_DMax, F_DMin, N_sampleSize, N_samples, doPrint)
    :return: Samples, Means
    """
    mean_ln, sig_ln, D_Min, D_Max, F_DMax, F_DMin, N_sampleSize, N_samples, doPrint = args
    Samples = []
    Means = []
    for n in range(N_samples):
        sample = makeSample((mean_ln, sig_ln, D_Min, D_Max, F_DMax, F_DMin), N=N_sampleSize)
        Samples.append(sample)
        sample_Stats = sampleStats(sample)
        Means.append(sample_Stats[0])
        if doPrint:
            print(f"Sample {n}: mean = {sample_Stats[0]:0.3f}, var = {sample_Stats[1]:0.3f}")
    return Samples, Means


def main():
    '''
    Simulates a gravel production process where the initial distribution of rock sizes follows a log-normal distribution
    that is sieved between two screens. It then randomly samples from the truncated distribution to produce 11 samples of
    100 rocks each and computes the mean and variance of each sample as well as the mean and variance of the sampling mean.

    Assumptions:
    - Rocks are approximated as spherical.
    - Pre-sieved rock sizes follow a log-normal distribution with parameters μ and σ.
    - Post-sieving, the distribution is truncated between Dmin and Dmax.

    Uses SciPy's quad for integration and fsolve for solving the inverse CDF.
    :return: nothing
    '''
    # Setup default values
    mean_ln = math.log(2)  # units in inches
    sig_ln = 1
    D_Max = 1
    D_Min = 3.0 / 8.0
    N_samples = 11
    N_sampleSize = 100
    goAgain = True

    while goAgain:
        # Get user inputs for parameters
        mean_ln, sig_ln = getPreSievedParameters((mean_ln, sig_ln))
        D_Min, D_Max = getSieveParameters((D_Min, D_Max))
        N_samples, N_sampleSize = getSampleParameters((N_samples, N_sampleSize))
        F_DMin, F_DMax = getFDMaxFDMin((mean_ln, sig_ln, D_Min, D_Max))

        # Optionally, plotting code is commented out
        # x = [_x*0.1 for _x in range(0,100)]
        # y = [ln_PDF((_x, mean_ln, sig_ln)) for _x in x]
        # x_trunc = [D_Min + _x*(D_Max-D_Min)/99 for _x in range(100)]
        # y_trunc = [ln_PDF((_x, mean_ln, sig_ln))/(F_DMax-F_DMin) for _x in x_trunc]
        # fig, ax1 = plt.subplots()
        # ax1.plot(x, y)
        # ax2 = ax1.twinx()
        # ax2.plot(x_trunc, y_trunc)
        # plt.show()

        # Create samples and compute sample statistics
        Samples, Means = makeSamples((mean_ln, sig_ln, D_Min, D_Max, F_DMax, F_DMin, N_sampleSize, N_samples, True))

        # Compute statistics for the sampling mean
        stats_of_Means = sampleStats(Means)
        print(f"Mean of the sampling mean:  {stats_of_Means[0]:0.3f}")
        print(f"Variance of the sampling mean:  {stats_of_Means[1]:0.6f}")
        goAgain = input('Go again? (No)').strip().lower().__contains__('y')


# endregion

if __name__ == '__main__':
    main()