import torch 
import torch.nn as nn
import torch.optim as optim


class DQN(nn.Module):

    def __init__(self, input_size, output_size, optim_lr=0.0001):
        super(DQN, self).__init__()

        # what should this architecture be?
        self.dense1 = nn.Linear(input_size, 32)
        self.relu1 = nn.ReLU()
        self.dense2 = nn.Linear(32, 32)
        self.relu2 = nn.ReLU()
        self.out_dense = nn.Linear(32, output_size)

        self.optimizer = optim.Adam(self.parameters(), lr=optim_lr)
        self.criteria = nn.MSELoss()
        self.loss = None

    def forward(self, input_data):
        x = self.dense1(input_data)
        x = self.relu1(x)
        x = self.dense2(x)
        x = self.relu2(x)
        x = self.out_dense(x)

        return x

    def compute_loss(self, outputs, targets):
        self.loss = self.criteria(outputs, targets)

    def update_params(self):
        self.optimizer.zero_grad()
        self.loss.backward(retain_graph=True)  
        self.optimizer.step()


if __name__ == "__main__":
    # init net with input size of 4 and output size of 2
    net = DQN(4, 2)

    # fwd pass
    out = net.forward(torch.randn(4))

    # imaginary output targets
    targets = torch.randn(2)

    # loss and backprop
    net.compute_loss(out, targets)
    net.update_params()

