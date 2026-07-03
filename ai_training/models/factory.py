import timm
import torch.nn as nn

def create_model(model_name: str, num_classes: int = 2, pretrained: bool = True):
    """
    Architecture-agnostic model factory utilizing PyTorch Image Models (timm).
    Allows easy switching between backbones like 'resnet50', 'efficientnet_b4', etc.
    """
    model = timm.create_model(model_name, pretrained=pretrained, num_classes=num_classes)
    return model

if __name__ == "__main__":
    # Test factory
    try:
        model = create_model("resnet18", num_classes=2, pretrained=False)
        print(f"Successfully instantiated resnet18. Output shape: {model(timm.utils.torch.randn(1, 3, 224, 224)).shape}")
    except Exception as e:
        print(f"Failed to instantiate model: {e}")
