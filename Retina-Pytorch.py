# -*- coding: utf-8 -*-
"""RetinaNet Pytorch.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1OuhZ87yzDz0sxXZasCaepYAxYZwwxRaf

# **Loading Dataset**
"""

!wget http://images.cocodataset.org/zips/val2017.zip
!unzip val2017.zip
!wget http://images.cocodataset.org/annotations/annotations_trainval2017.zip
!unzip annotations_trainval2017.zip

"""# **Loading Model**"""

device='cuda'

import torch
import torchvision

model = torchvision.models.detection.retinanet_resnet50_fpn_v2(pretrained=True).to(device)
model.eval()

"""# **Helper Functions**"""

from torchvision.datasets import CocoDetection

coco = CocoDetection(root='/content/val2017',
                     annFile='/content/annotations/instances_val2017.json')

from torchvision import transforms

def preprocess(image):
    transform = transforms.Compose([
        transforms.ToTensor(),
    ])
    return transform(image)

from pycocotools.coco import COCO
from torchvision.utils import draw_bounding_boxes
import matplotlib.pyplot as plt
import numpy as np
import cv2

def predictAndPlot(model, image, image_id):
    with torch.no_grad():
        image_tensor = preprocess(image).unsqueeze(0)
        imgCopy=torch.tensor(255*(preprocess(image)),dtype=torch.uint8)
        predictions = model(image_tensor.to(device))
        
    scores = predictions[0]['scores'].cpu().numpy()
    boxes = predictions[0]['boxes'].cpu().numpy()
    labels = predictions[0]['labels'].cpu().numpy()

    bbImg=draw_bounding_boxes(imgCopy,predictions[0]['boxes'][predictions[0]['scores']>0.7],width=8)
    plt.imshow(bbImg.permute(1,2,0))
    plt.show()
    
    result = []
    for score, box, label in zip(scores, boxes, labels):
        x1, y1, x2, y2 = box

        if(score>=0.5):

          result.append({
              'image_id': image_id,
              'category_id': label,
              'bbox': [x1, y1, x2 - x1, y2 - y1],
              'score': score
          })
    
    return result

def predict(model, image, image_id):
    with torch.no_grad():
        image_tensor = preprocess(image).unsqueeze(0)
        predictions = model(image_tensor.to(device))
        
    scores = predictions[0]['scores'].cpu().numpy()
    boxes = predictions[0]['boxes'].cpu().numpy()
    labels = predictions[0]['labels'].cpu().numpy()
    
    result = []
    for score, box, label in zip(scores, boxes, labels):
        x1, y1, x2, y2 = box

        if(score>=0.7):

          result.append({
              'image_id': image_id,
              'category_id': label,
              'bbox': [x1, y1, x2 - x1, y2 - y1],
              'score': score
          })
    
    return result

"""# **Inference on val2017 split (5k images)**"""

from tqdm import tqdm
results = []
imageIds=[]
for i in tqdm(range(len(coco))):
  image, target = coco[i]
  imgId=coco.ids[i]
  imageIds.append(imgId)
  result = predict(model, image, imgId)
  results.extend(result)
    
print(results)

"""# **Evaluation**"""

from pycocotools.cocoeval import COCOeval

coco_gt = COCO('/content/annotations/instances_val2017.json')

coco_results = coco_gt.loadRes(results)
coco_eval = COCOeval(coco_gt, coco_results, iouType='bbox')
coco_eval.evaluate()
coco_eval.accumulate()
coco_eval.summarize()

"""# **Visual Samples**"""

idx=896
image, target = coco[idx]
imgId=target[0]['image_id']
imageIds.append(imgId)
result = predictAndPlot(model, image, imgId)

idx=467
image, target = coco[idx]
imgId=target[0]['image_id']
imageIds.append(imgId)
result = predictAndPlot(model, image, imgId)

idx=408
image, target = coco[idx]
imgId=target[0]['image_id']
imageIds.append(imgId)
result = predictAndPlot(model, image, imgId)

idx=850
image, target = coco[idx]
imgId=target[0]['image_id']
imageIds.append(imgId)
result = predictAndPlot(model, image, imgId)