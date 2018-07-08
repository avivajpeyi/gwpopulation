from __future__ import division, print_function
from tupak.hyper.likelihood import HyperparameterLikelihood
import numpy as np
import models


class RateLikelihood(HyperparameterLikelihood):
    """ A likelihood for infering hyperparameter posterior distributions and
    rate estimates

    See Eq. (1) of https://arxiv.org/abs/1801.02699, Eq. (4)
    https://arxiv.org/abs/1805.06442 for a definition.

    Parameters
    ----------
    posteriors: list
        An list of pandas data frames of samples sets of samples. Each set may have
        a different size.
    hyper_prior: func
        Function which calculates the new prior probability for the data.
    sampling_prior: func
        Function which calculates the prior probability used to sample.
    max_samples: int
        Maximum number of samples to use from each set.

    """

    def __init__(self, posteriors, hyper_prior, sampling_prior, max_samples=1e100, analysis_time=1):
        super(RateLikelihood, self).__init__(posteriors, hyper_prior, sampling_prior, max_samples)
        self.analysis_time = analysis_time

    def log_likelihood(self):
        log_l = HyperparameterLikelihood.log_likelihood(self)
        log_l += self.n_posteriors * np.log(self.parameters['rate'])
        log_l -= models.norm_vt(self.parameters) * self.parameters['rate'] * self.analysis_time
        return np.nan_to_num(log_l)


class Model(object):
    """
    Population model

    This should take population parameters and return the probability.
    """

    def __init__(self, model_functions=None):
        """
        Parameters
        ----------
        model_functions: list
            List of functions to compute.
        """
        self.models = model_functions

        self.parameters = dict()
        for function in self.models:
            for key in function.func_code.co_varnames[1:function.func_code.co_argcount]:
                self.parameters[key] = None

    def prob(self, data):
        if isinstance(data, dict):
            probability = np.ones_like(data.values()[0])
        else:
            probability = np.ones_like(data.values())
        for function in self.models:
            probability *= function(data, **self._get_function_parameters(function))
        return probability

    def _get_function_parameters(self, function):
        parameters = {key: self.parameters[key] for key in
                      function.func_code.co_varnames[1:function.func_code.co_argcount]}
        return parameters
