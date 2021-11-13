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

import torch
import torch.nn as nn
import random
import numpy as np
import cv2
from types import SimpleNamespace

from app.stargan.model import build_model
from app.stargan.checkpoint import CheckpointIO
import app.stargan.utils as utils
from torchvision import transforms
from PIL import Image

args = SimpleNamespace()
args.confidence = 0.5
net = cv2.dnn.readNetFromCaffe('stargan/deploy.prototxt.txt', 'stargan/res10_300x300_ssd_iter_140000.caffemodel')

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

    def crop_face(self, cv2_img, pil_img):
        nparr = np.fromstring(cv2_img, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
        net.setInput(blob)
        detections = net.forward()
        w, h = pil_img.size
        confidence = detections[0, 0, 0, 2]
        if confidence > 0.8:
            box = detections[0, 0, 0, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            startX = startX - (endX - startX) * 0.2 if startX - (endX - startX) * 0.2 > 0 else 0
            startY = startY - (endY - startY) * 0.15 if startY - (endY - startY) * 0.15 > 0 else 0
            endX = endX + (endX - startX) * 0.2 if endX + (endX - startX) * 0.2 < w else w
            endY = endY + (endY - startY) * 0.15 if endY + (endY - startY) * 0.15 < h else h
            return pil_img.crop((startX, startY, endX, endY))
        else:
            # no detected face
            return 0

    def style(self, cv2_img, pil_img, target_sex):
        nets_ema = self.nets_ema
        if target_sex == 0:
            style_img = Image.open("stargan/198523.jpeg")
        else:
            style_img = Image.open("stargan/038044.jpeg")
        pil_img = self.crop_face(cv2_img, pil_img)
        if pil_img != 0:
            return generate(nets_ema, style_img, pil_img, target_sex)
        else:
            return "ERROR"

    @torch.no_grad()
    def ref(self, pil_ref, pil_src, cv2_ref, cv2_src, target_sex):
        nets_ema = self.nets_ema
        print("REF")
        ref_img = self.crop_face(cv2_ref, pil_ref)
        print("SRC")
        src_img = self.crop_face(cv2_src, pil_src)
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
    masks = nets.fan.get_heatmap(src)
    s_trg = nets.style_encoder(ref, y_trg).to(device)
    x_fake = nets.generator(src, s_trg, masks=masks)
    return transforms.ToPILImage()(denormalize(x_fake[0])).convert("RGB")
