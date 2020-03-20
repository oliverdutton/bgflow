import numpy as np
import torch

def kernelize_with_rbf(d, mu, gamma=1.0, eps=1e-6):
    """
    Takes a distance matrix `d` of shape

        `[n_batch, n_particles, n_particles, 1]`

    and maps it onto a normalized radial basis function (RBF) kernel
    representation of shape

        `[n_batch, n_particles, n_particles, n_kernels]`

    via

        `d_{ij} -> f_{ij}

    where

        `f_{ij} = (g_{ij1}, ..., g_{ijK}) / sum_{k} g_{ijk}

    and

        `g_{ijk} = exp(-(d_{ij} - mu_{k})^{2} / gamma^{2})`.


    Parameters
    ----------
    d: PyTorch tensor
        distance matrix of shape `[n_batch, n_particles, n_particles, 1]`
    mu: PyTorch tensor / scalar
        Means of RBF kernels. Either of shape `[1, 1, 1, n_kernels]` or
        scalar
    gamma: PyTorch tensor / scalar
        Bandwidth of RBF kernels. Either same shape as `mu` or scalar.

    Returns
    -------
    rbfs: PyTorch tensor
        RBF representation of distance matrix of shape
        `[n_batch, n_particles, n_particles, n_kernels]`

    Examples
    --------
    """
    rbfs = torch.exp(-(d - mu).pow(2) / gamma ** 2) + eps
    rbfs = rbfs / rbfs.sum(dim=-1, keepdim=True)
    return rbfs


def compute_gammas(mus, gain=1.0):
    isize = mus[..., [-1]] - mus[..., [0]]
    n_kernels = sum(mus.shape)
    gammas = torch.ones_like(mus) * gain * isize / np.sqrt(n_kernels)
    return gammas


class RbfEncoder(torch.nn.Module):
    def __init__(self, mus, log_gammas, trainable=True):
        super().__init__()
        self._mus = mus
        self._log_gammas = log_gammas
        if trainable:
            self._mus = torch.nn.Parameter(self._mus)
            self._log_gammas = torch.nn.Parameter(self._log_gammas)

    def forward(self, d):
        gammas = self._log_gammas.exp()
        return kernelize_with_rbf(d, self._mus, gammas)


def rbf_kernels(d, mu, neg_log_gamma, derivative=False):
    inv_gamma = torch.exp(neg_log_gamma)
    rbfs = torch.exp(-(d - mu).pow(2) * inv_gamma.pow(2))
    srbfs = rbfs.sum(dim=-1, keepdim=True)
    kernels = rbfs / (1e-6 + srbfs)
    if derivative:
        drbfs = -2 * (d - mu) * inv_gamma.pow(2) * rbfs
        sdrbfs = drbfs.sum(dim=-1, keepdim=True)
        dkernels = drbfs / (1e-6 + srbfs) - rbfs * sdrbfs / (1e-6 + srbfs ** 2)
    else:
        dkernels = None
    return kernels, dkernels