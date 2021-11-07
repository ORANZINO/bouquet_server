"""
StarGAN v2
Copyright (c) 2020-present NAVER Corp.

This work is licensed under the Creative Commons Attribution-NonCommercial
4.0 International License. To view a copy of this license, visit
http://creativecommons.org/licenses/by-nc/4.0/ or send a letter to
Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
"""

import os
from os.path import join as ospj
from munch import Munch

import torch
import torch.nn as nn
import torch.nn.functional as F

from app.stargan.model import build_model
from app.stargan.checkpoint import CheckpointIO
import app.stargan.utils as utils
from torchvision import transforms
from PIL import Image


class Solver(nn.Module):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        self.nets_ema = build_model(args)

        for name, module in self.nets_ema.items():
            setattr(self, name + '_ema', module)

        self.ckptios = [CheckpointIO(ospj(args.checkpoint_dir, 'nets_ema.ckpt'), data_parallel=True, **self.nets_ema)]

        self.to(self.device)
        for name, network in self.named_children():
            # Do not initialize the FAN parameters
            if ('ema' not in name) and ('fan' not in name):
                print('Initializing %s...' % name)
                network.apply(utils.he_init)
        self._load_checkpoint()

    def _load_checkpoint(self):
        for ckptio in self.ckptios:
            ckptio.load()

    def _reset_grad(self):
        for optim in self.optims.values():
            optim.zero_grad()
        
    @torch.no_grad()
    def style(self, img, target_sex):
        nets_ema = self.nets_ema
        style_img = Image.open("stargan/005923.jpeg")
        return generate(nets_ema, style_img, img, target_sex)

    @torch.no_grad()
    def ref(self, ref_img, src_img, target_sex):
        nets_ema = self.nets_ema
        return generate(nets_ema, ref_img, src_img, target_sex)


def denormalize(x):
    out = (x + 1) / 2
    return out.clamp_(0, 1)


def generate(nets, ref, src, target_sex, img_size=256):
    print('Generating images...')
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    mean = [0.5, 0.5, 0.5]
    std = [0.5, 0.5, 0.5]
    transform = transforms.Compose([
        transforms.Resize([img_size, img_size]),
        transforms.ToTensor(),
        transforms.Normalize(mean=mean, std=std)
    ])
    ref = transform(ref).unsqueeze(0).to(device)
    src = transform(src).unsqueeze(0).to(device)
    y_trg = torch.tensor([target_sex]).to(device)
    masks = nets.fan.get_heatmap(src).to(device)
    s_trg = nets.style_encoder(ref, y_trg).to(device)
    x_fake = nets.generator(src, s_trg, masks=masks)
    return transforms.ToPILImage()(denormalize(x_fake[0])).convert("RGB")
