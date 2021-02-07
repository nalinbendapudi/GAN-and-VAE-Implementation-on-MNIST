from __future__ import print_function
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import torch
import torch.utils.data
from torch import nn, optim
from torch.autograd import Variable
from torch.nn import functional as F
from torchvision import datasets, transforms
from torchvision.utils import save_image


def hello_vae():
    print("Hello from vae.py!")


class VAE(nn.Module):
    def __init__(self, input_size, latent_size=15):
        super(VAE, self).__init__()
        self.input_size = input_size # 28*28
        self.latent_size = latent_size # Z
        self.hidden_dim = None # H
        self.encoder = None
        self.mu_layer = None
        self.logvar_layer = None
        self.decoder = None

        ############################################################################################
        # TODO: Implement the fully-connected encoder architecture described in the notebook.      #
        # Specifically, self.encoder should be a network that inputs a batch of input images of    #
        # shape (N, 1, H, W) into a batch of hidden features of shape (N, H). Set up self.mu_layer #
        # and self.logvar_layer to be a pair of linear layers that map the hidden features into    #
        # estimates of the mean and variance of the posterior over the latent vectors; the mean    #
        # and variance estimates will both be tensors of shape (N, Z).                             #
        ############################################################################################
        # Replace "pass" statement with your code
        
        self.hidden_dim = 150     # hyper-parameter
        
        self.encoder = nn.Sequential(
          nn.Flatten(),
          nn.Linear(self.input_size, self.hidden_dim),
          nn.ReLU(),
          nn.Linear(self.hidden_dim, self.hidden_dim),
          nn.ReLU(),
          nn.Linear(self.hidden_dim, self.hidden_dim),
          nn.ReLU(),
        )

        self.mu_layer = nn.Linear(self.hidden_dim,self.latent_size)

        self.logvar_layer = nn.Linear(self.hidden_dim, self.latent_size)
      
        ############################################################################################
        # TODO: Implement the fully-connected decoder architecture described in the notebook.      #
        # Specifically, self.decoder should be a network that inputs a batch of latent vectors of  #
        # shape (N, Z) and outputs a tensor of estimated images of shape (N, 1, H, W).             #
        ############################################################################################
        # Replace "pass" statement with your code
        
        img_w = int(self.input_size**(1/2))
        img_h = int(self.input_size**(1/2))

        self.decoder = nn.Sequential(
          nn.Linear(self.latent_size,self.hidden_dim),
          nn.ReLU(),
          nn.Linear(self.hidden_dim, self.hidden_dim),
          nn.ReLU(),
          nn.Linear(self.hidden_dim, self.hidden_dim),
          nn.ReLU(),
          nn.Linear(self.hidden_dim, self.input_size),
          nn.Sigmoid(),
          nn.Unflatten(1,(1,img_w, img_h))
        )

        ############################################################################################
        #                                      END OF YOUR CODE                                    #
        ############################################################################################


    def forward(self, x):
        """
        Performs forward pass through FC-VAE model by passing image through 
        encoder, reparametrize trick, and decoder models
    
        Inputs:
        - x: Batch of input images of shape (N, 1, H, W)
        
        Returns:
        - x_hat: Reconstruced input data of shape (N,1,H,W)
        - mu: Matrix representing estimated posterior mu (N, Z), with Z latent space dimension
        - logvar: Matrix representing estimataed variance in log-space (N, Z), with Z latent space dimension
        """
        x_hat = None
        mu = None
        logvar = None
        ############################################################################################
        # TODO: Implement the forward pass by following these steps                                #
        # (1) Pass the input batch through the encoder model to get posterior mu and logvariance   #
        # (2) Reparametrize to compute  the latent vector z                                        #
        # (3) Pass z through the decoder to resconstruct x                                         #
        ############################################################################################
        # Replace "pass" statement with your code
        
        hidden = self.encoder(x)
        mu = self.mu_layer(hidden)
        logvar = self.logvar_layer(hidden)

        z = reparametrize(mu,logvar)

        x_hat = self.decoder(z)

        ############################################################################################
        #                                      END OF YOUR CODE                                    #
        ############################################################################################
        return x_hat, mu, logvar


class CVAE(nn.Module):
    def __init__(self, input_size, num_classes=10, latent_size=15):
        super(CVAE, self).__init__()
        self.input_size = input_size # # 28*28
        self.latent_size = latent_size # Z
        self.num_classes = num_classes # C
        self.hidden_dim = None # H
        self.encoder = None
        self.mu_layer = None
        self.logvar_layer = None
        self.decoder = None

        ############################################################################################
        # TODO: Define a FC encoder as described in the notebook that transforms the image         #
        # (N, 1, H, W) into a hidden_dimension (N, H) feature space, and a final two layers that   #
        # project that feature map (after flattening and now adding our one-hot class vector) to   #
        # posterior mu and posterior variance estimates of the latent space (N, Z)                 #
        ############################################################################################
        # Replace "pass" statement with your code
        
        self.hidden_dim = 150     # hyper-parameter
        
        self.encoder = nn.Sequential(
          nn.Linear(self.input_size + self.num_classes, self.hidden_dim),
          nn.ReLU(),
          nn.Linear(self.hidden_dim, self.hidden_dim),
          nn.ReLU(),
          nn.Linear(self.hidden_dim, self.hidden_dim),
          nn.ReLU(),
        )

        self.mu_layer = nn.Linear(self.hidden_dim,self.latent_size)

        self.logvar_layer = nn.Linear(self.hidden_dim, self.latent_size)
      
        ############################################################################################
        # TODO: Define a fully-connected decoder as described in the notebook that transforms the  #
        # latent space (N, Z + C) to the D input dimension                                         #
        ############################################################################################
        # Replace "pass" statement with your code
        
        img_w = int(self.input_size**(1/2))
        img_h = int(self.input_size**(1/2))

        self.decoder = nn.Sequential(
          nn.Linear(self.latent_size + self.num_classes, self.hidden_dim),
          nn.ReLU(),
          nn.Linear(self.hidden_dim, self.hidden_dim),
          nn.ReLU(),
          nn.Linear(self.hidden_dim, self.hidden_dim),
          nn.ReLU(),
          nn.Linear(self.hidden_dim, self.input_size),
          nn.Sigmoid(),
          nn.Unflatten(1,(1,img_w, img_h))
        )
        ############################################################################################
        #                                      END OF YOUR CODE                                    #
        ############################################################################################

    def forward(self, x, c):
        """
        Performs forward pass through FC-CVAE model by passing image through 
        encoder, reparametrize trick, and decoder models
    
        Inputs:
        - x: Input data for this timestep of shape (N,1,H,W)
        - c: One hot vector representing the input class (0-9) (N, C)
        
        Returns:
        - x_hat: Reconstruced input data of shape (N,1,H,W)
        - mu: Matrix representing estimated posterior mu (N, Z), with Z latent space dimension
        - logvar: Matrix representing estimated variance in log-space (N, Z),  with Z latent space dimension
        """
        x_hat = None
        mu = None
        logvar = None
        ############################################################################################
        # TODO: Implement the forward pass by following these steps                                #
        # (1) Pass the input batch through the encoder model to get posterior mu and logvariance   #
        # (2) Reparametrize to compute  the latent vector z                                        #
        # (3) Pass z through the decoder to resconstruct x                                         #
        ############################################################################################
        # Replace "pass" statement with your code
        
        N = x.shape[0]
        img_and_class = torch.cat( (x.view(N,-1),c) , dim=1)

        hidden = self.encoder(img_and_class)
        mu = self.mu_layer(hidden)
        logvar = self.logvar_layer(hidden)

        z = reparametrize(mu,logvar)

        latent_and_class = torch.cat( (z,c) , dim=1)

        x_hat = self.decoder(latent_and_class)

        ############################################################################################
        #                                      END OF YOUR CODE                                    #
        ############################################################################################
        return x_hat, mu, logvar



def reparametrize(mu, logvar):
    """
    Differentiably sample random Gaussian data with specified mean and variance using the
    reparameterization trick.

    Suppose we want to sample a random number z from a Gaussian distribution with mean mu and
    standard deviation sigma, such that we can backpropagate from the z back to mu and sigma.
    We can achieve this by first sampling a random value epsilon from a standard Gaussian
    distribution with zero mean and unit variance, then setting z = sigma * epsilon + mu.

    For more stable training when integrating this function into a neural network, it helps to
    pass this function the log of the variance of the distribution from which to sample, rather
    than specifying the standard deviation directly.

    Inputs:
    - mu: Tensor of shape (N, Z) giving means
    - logvar: Tensor of shape (N, Z) giving log-variances

    Returns: 
    - z: Estimated latent vectors, where z[i, j] is a random value sampled from a Gaussian with
         mean mu[i, j] and log-variance logvar[i, j].
    """
    z = None
    ################################################################################################
    # TODO: Reparametrize by initializing epsilon as a normal distribution and scaling by          #
    # posterior mu and sigma to estimate z                                                         #
    ################################################################################################
    # Replace "pass" statement with your code
    
    N,Z = mu.shape
    
    sigma = torch.exp(logvar/2)

    z = torch.randn(N,Z, device=mu.device, dtype=mu.dtype) * sigma + mu
    
    ################################################################################################
    #                              END OF YOUR CODE                                                #
    ################################################################################################
    return z


def loss_function(x_hat, x, mu, logvar):
    """
    Computes the variational lower bound loss term of the VAE (refer to formulation in notebook).

    Inputs:
    - x_hat: Reconstruced input data of shape (N, 1, H, W)
    - x: Input data for this timestep of shape (N, 1, H, W)
    - mu: Matrix representing estimated posterior mu (N, Z), with Z latent space dimension
    - logvar: Matrix representing estimataed variance in log-space (N, Z), with Z latent space dimension
    
    Returns:
    - loss: Tensor containing the scalar loss for the variational lowerbound
    """
    loss = None
    ################################################################################################
    # TODO: Compute variational lowerbound loss as described in the notebook                       #
    ################################################################################################
    # Replace "pass" statement with your code
    N = x.shape[0]
    
    reconstruction_loss = nn.functional.binary_cross_entropy(x_hat, x, reduction='sum') / N
    KL_divergence_loss = 0.5 * (1+logvar-mu**2-torch.exp(logvar)).sum() / N

    loss = reconstruction_loss - KL_divergence_loss

    ################################################################################################
    #                            END OF YOUR CODE                                                  #
    ################################################################################################
    return loss

