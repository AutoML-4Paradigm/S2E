import torch 
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
import numpy as np

# Loss functions
def loss_coteaching(y_1, y_2, t, forget_rate, ind, noise_or_not):
    loss_1 = F.cross_entropy(y_1, t, reduce = False)
    ind_1_sorted = np.argsort(loss_1.data).cuda()
    loss_1_sorted = loss_1[ind_1_sorted]

    loss_2 = F.cross_entropy(y_2, t, reduce = False)
    ind_2_sorted = np.argsort(loss_2.data).cuda()
    loss_2_sorted = loss_2[ind_2_sorted]

    remember_rate = 1 - forget_rate
    num_remember = int(remember_rate * len(loss_1_sorted))

    pure_ratio_1 = np.sum(noise_or_not[ind[ind_1_sorted[:num_remember]]])/float(num_remember)
    pure_ratio_2 = np.sum(noise_or_not[ind[ind_2_sorted[:num_remember]]])/float(num_remember)

    ind_1_update=ind_1_sorted[:num_remember]
    ind_2_update=ind_2_sorted[:num_remember]
    # exchange
    loss_1_update = F.cross_entropy(y_1[ind_2_update], t[ind_2_update])
    loss_2_update = F.cross_entropy(y_2[ind_1_update], t[ind_1_update])

    return torch.sum(loss_1_update)/num_remember, torch.sum(loss_2_update)/num_remember, pure_ratio_1, pure_ratio_2

def loss_weighted(y_1, y_2, t, forget_rate, ind, noise_or_not):
    loss_1 = torch.Tensor(F.cross_entropy(y_1, t, reduce = False))
    loss_2 = torch.Tensor(F.cross_entropy(y_2, t, reduce = False))
    weight=1/(1+(loss_1-loss_2)*(loss_1-loss_2))

    # exchange
    loss_1_update = weight*F.cross_entropy(y_1, t, reduce = False)
    loss_2_update = weight*F.cross_entropy(y_2, t, reduce = False)

    return torch.sum(loss_1_update)/len(loss_1), torch.sum(loss_2_update)/len(loss_2)

def loss_3teaching(y_1, y_2, y_3, t, forget_rate, ind, noise_or_not):
    loss_1 = F.cross_entropy(y_1, t, reduce = False)
    ind_1_sorted = np.argsort(loss_1.data).cuda()
    loss_1_sorted = loss_1[ind_1_sorted]

    loss_2 = F.cross_entropy(y_2, t, reduce = False)
    ind_2_sorted = np.argsort(loss_2.data).cuda()
    loss_2_sorted = loss_2[ind_2_sorted]

    loss_3 = F.cross_entropy(y_3, t, reduce = False)
    ind_3_sorted = np.argsort(loss_3.data).cuda()
    loss_3_sorted = loss_3[ind_3_sorted]

    remember_rate = 1 - forget_rate
    num_remember = int(remember_rate * len(loss_1_sorted))

    pure_ratio_1 = np.sum(noise_or_not[ind[ind_1_sorted[:num_remember]]])/float(num_remember)
    pure_ratio_2 = np.sum(noise_or_not[ind[ind_2_sorted[:num_remember]]])/float(num_remember)
    pure_ratio_3 = np.sum(noise_or_not[ind[ind_3_sorted[:num_remember]]])/float(num_remember)

    ind_1_update=np.intersect1d(ind_2_sorted[:num_remember],ind_3_sorted[:num_remember],assume_unique=True)
    ind_2_update=np.intersect1d(ind_3_sorted[:num_remember],ind_1_sorted[:num_remember],assume_unique=True)
    ind_3_update=np.intersect1d(ind_1_sorted[:num_remember],ind_2_sorted[:num_remember],assume_unique=True)
    # exchange
    loss_1_update = F.cross_entropy(y_1[ind_1_update], t[ind_1_update])
    loss_2_update = F.cross_entropy(y_2[ind_2_update], t[ind_2_update])
    loss_3_update = F.cross_entropy(y_3[ind_3_update], t[ind_3_update])

    return torch.sum(loss_1_update)/num_remember, torch.sum(loss_2_update)/num_remember, torch.sum(loss_3_update)/num_remember, pure_ratio_1, pure_ratio_2, pure_ratio_3
