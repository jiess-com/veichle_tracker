import torch
import torch.nn as nn
import torch.nn.functional as F
from cv2.dnn import Net


# resnet-block
class ResBlock(nn.Module):
    def __init__(self, inc, ksize):
        super(ResBlock, self).__init__()
        pad = (ksize - 1)//2
        self.net = nn.Sequential(nn.Conv2d(inc,inc,ksize,1,pad),
                                 nn.ReLU(),
                                 nn.Conv2d(inc,inc,ksize,1,pad))
    def forward(self, x):
        return x + self.net(x)

# create as the author's code
class ConvLSTM(nn.Module):
    def __init__(self):
        super(ConvLSTM, self).__init__()
        self.conv = nn.Conv2d(256, 512, 3, 1, 1)

    def forward(self, x, h, c):
        res = self.conv(torch.cat([x, h], 1))
        i, j, f, o = res.split(128, 1)
        i = i.sigmoid()
        j = j.tanh()
        f = torch.sigmoid(f + 1.0)
        o = o.sigmoid()
        new_c = c * f + i * j
        new_h = new_c.tanh() * o
        return new_h, new_c

    def init_hidden_state(self, N, C, H, W):
        return (torch.zeros(N,C,H,W),torch.zeros(N,C,H,W))

# create as the author's code
class LstmNet(nn.Module):
    def __init__(self):
        super(LstmNet, self).__init__()
        eblk1 = [nn.Conv2d(2, 32, 5, 1, 2), nn.ReLU(),
                 ResBlock(32, 5),
                 ResBlock(32, 5),
                 ResBlock(32, 5)]
        eblk2 = [nn.Conv2d(32, 64, 5, 2, 2), nn.ReLU(),
                 ResBlock(64, 5),
                 ResBlock(64, 5),
                 ResBlock(64, 5)]
        eblk3 = [nn.Conv2d(64, 128, 5, 2, 2), nn.ReLU(),
                 ResBlock(128, 5),
                 ResBlock(128, 5),
                 ResBlock(128, 5)]
        self.encoder1 = nn.Sequential(*eblk1)
        self.encoder2 = nn.Sequential(*eblk2)
        self.encoder3 = nn.Sequential(*eblk3)
        dblk3 = [ResBlock(128, 5),
                 ResBlock(128, 5),
                 ResBlock(128, 5),
                 nn.ConvTranspose2d(128, 64, 4, 2, 1),
                 nn.ReLU()]
        dblk2 = [ResBlock(64, 5),
                 ResBlock(64, 5),
                 ResBlock(64, 5),
                 nn.ConvTranspose2d(64, 32, 4, 2, 1),
                 nn.ReLU()]
        dblk1 = [ResBlock(32, 5),
                 ResBlock(32, 5),
                 ResBlock(32, 5),
                 nn.Conv2d(32, 1, 5, 1, 2)]
        self.decoder1 = nn.Sequential(*dblk1)
        self.decoder2 = nn.Sequential(*dblk2)
        self.decoder3 = nn.Sequential(*dblk3)
        self.convlstm = ConvLSTM()

    def _step_(self, x, h, c):
        e32 = self.encoder1(x)
        e64 = self.encoder2(e32)
        e128 = self.encoder3(e64)
        h, c = self.convlstm(e128, h, c)
        d64  = self.decoder3(h)
        d32  = self.decoder2(d64 + e64)
        d3   = self.decoder1(d32 + e32)
        return d3, h, c

    def forward(self, x1, x2, x4):
        N, _, H, W = x4.size()
        h, c  = self.convlstm.init_hidden_state(N,128,H//4,W//4)
        i4, h, c = self._step_(torch.cat([x4, x4], 1), h, c)
        output = [i4]

        h  = F.interpolate(h, scale_factor=2, mode='bilinear')
        c  = F.interpolate(c, scale_factor=2, mode='bilinear')
        i4 = F.interpolate(i4, scale_factor=2, mode='bilinear')
        i2, h, c = self._step_(torch.cat([x2, i4], 1), h, c)
        output.append(i2)

        h  = F.interpolate(h, scale_factor=2, mode='bilinear')
        c  = F.interpolate(c, scale_factor=2, mode='bilinear')
        i2 = F.interpolate(i2, scale_factor=2, mode='bilinear')
        i1, h, c = self._step_(torch.cat([x1, i2], 1), h, c)
        output.append(i1)
        return output

def demo():
    x1 = torch.randn(4, 3, 128, 128)
    x2 = torch.randn(4, 3, 64, 64)
    x4 = torch.randn(4, 3, 32, 32)
    model = Net().eval()

    with torch.no_grad():
        output = model(x1, x2, x4)
    print('1/4: {}'.format(output[0].size()))
    print('1/2: {}'.format(output[1].size()))
    print('1/1: {}'.format(output[2].size()))

if __name__ == "__main__":
    demo()