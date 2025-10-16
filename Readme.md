## Instructions to Run the MiDaS and SAM solution

## Step 1: Installing libraries
Run the pip command to install required libraries
```shell
pip install -r requirements.txt
```

## Step 2: Installing MiDaS and SAM models

MiDaS is available on torch hub. Run the follwing cell if not present
```python
import torch
model_type = "DPT_Large"     # MiDaS v3 - Large     (highest accuracy, slowest inference speed)
#model_type = "DPT_Hybrid"   # MiDaS v3 - Hybrid    (medium accuracy, medium inference speed)
#model_type = "MiDaS_small"  # MiDaS v2.1 - Small   (lowest accuracy, highest inference speed)

midas = torch.hub.load("intel-isl/MiDaS", model_type)
```
If GPU accleration is available:
```python
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
midas.to(device)
midas.eval()
```
Comment model_type according to requirement


SAM has a github repo. To install, run the following command (Make sure Git is installed on machine)
```shell
pip install git+https://github.com/facebookresearch/segment-anything.git
```
SAM needs a checkpoint to run. If checkpoints folder is empty goto this link and download any available checpoints:
[here](https://github.com/facebookresearch/segment-anything?tab=readme-ov-file#model-checkpoints)

create checkpoints folder
```python
import os
if not 'checkpoints' in os.listdir():
    os.mkdir('checkpoints')
```

## Step 3:

Add room and furniture images in images folder if not any present.
```python
filename = '<path/to/file>'
```

## Step 4:

Setup is done. Run all the cells in order.



