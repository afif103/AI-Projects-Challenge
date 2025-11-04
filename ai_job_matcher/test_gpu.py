# test_gpu.py
import torch
print(f"GPU: {torch.cuda.is_available()}")
print(f"Name: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")