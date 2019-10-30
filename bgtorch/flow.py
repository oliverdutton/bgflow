import torch

from .utils.types import is_list_or_tuple


class DiscreteFlow(torch.nn.Module):
    
    def __init__(self, layers):
        """
        Represents a diffeomorphism that can be computed
        as a discrete finite stack of layers.
        
        Returns the transformed variable and the log determinant
        of the Jacobian matrix.
            
        Parameters
        ----------
        layers : Tuple / List of flow layers
        """
        super().__init__()
        self._layers = torch.nn.ModuleList(layers)
    
    def forward(self, x, inverse=False):
        """
        Transforms the input along the diffeomorphism and returns
        the transformed variable together with the volume change.
            
        Parameters
        ----------
        x : PyTorch Floating Tensor.
            Input variable to be transformed. 
            Tensor of shape `[..., n_dimensions]`.
        inverse: boolean.
            Indicates whether forward or inverse transformation shall be performed.
            If `True` computes the inverse transformation.
        
        Returns
        -------
        z: PyTorch Floating Tensor.
            Transformed variable. 
            Tensor of shape `[..., n_dimensions]`.
        dlogp : PyTorch Floating Tensor.
            Total volume change as a result of the transformation.
            Corresponds to the log determinant of the Jacobian matrix.
        """
        dlogp = torch.zeros(*x.shape[:-1], 1).to(x)
        layers = self._layers
        if inverse:
            layers = reversed(layers)
        if not is_list_or_tuple(x):
            x = [x]
        for layer in layers:
            *x, ddlogp = layer(*x, inverse=inverse)
            dlogp += ddlogp
        return (*x, dlogp)