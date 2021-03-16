import torch


__all__ = ["Sampler"]


class Sampler(torch.nn.Module):
    
    def __init__(self):
        super().__init__()
    
    def _sample_with_temperature(self, n_samples, temperature):
        raise NotImplementedError()
        
    def _sample(self, n_samples):
        raise NotImplementedError()
    
    def sample(self, n_samples, temperature=1.0):
        if temperature != 1.0:
            return self._sample_with_temperature(n_samples, temperature)
        else:
            return self._sample(n_samples)