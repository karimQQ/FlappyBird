import torch
from torch.nn import Linear, ReLU, Sigmoid


class Model(torch.nn.Module):
    def __init__(self):
        super().__init__()

        # self.normalization = torch.nn.BatchNorm1d(1)
        self.linear1 = Linear(6, 12)
        self.activation1 = ReLU()
        self.linear2 = Linear(12, 8)
        self.activation2 = ReLU()
        self.linear3 = Linear(8, 4)
        self.activation3 = ReLU()
        self.linear4 = Linear(4, 1)

    def forward(self, x):
        # x = self.normalization(x)
        x = self.linear1(x)
        x = self.activation1(x)
        x = self.linear2(x)
        x = self.activation2(x)
        x = self.linear3(x)
        x = self.activation3(x)
        x = self.linear4(x)
        return x
