import os
from PIL import Image
from torch.utils.data import Dataset, DataLoader
import albumentations as A
from albumentations.pytorch import ToTensorV2
import numpy as np
import pandas as pd

class DeepfakeDataset(Dataset):
    def __init__(self, metadata_csv: str, img_dir: str, transform=None):
        """
        metadata_csv: path to CSV file containing 'filename' and 'label' (0 for real, 1 for fake)
        img_dir: root directory where processed images are stored
        """
        self.data = pd.read_csv(metadata_csv)
        self.img_dir = img_dir
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.data.iloc[idx]
        img_path = os.path.join(self.img_dir, row['path'])
        
        # Load image
        image = np.array(Image.open(img_path).convert("RGB"))
        label = int(row['label'])

        if self.transform:
            augmented = self.transform(image=image)
            image = augmented['image']

        return image, label

def get_transforms(img_size=224, is_train=True):
    if is_train:
        return A.Compose([
            A.Resize(img_size, img_size),
            A.HorizontalFlip(p=0.5),
            A.RandomBrightnessContrast(p=0.2),
            A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
            ToTensorV2()
        ])
    else:
        return A.Compose([
            A.Resize(img_size, img_size),
            A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
            ToTensorV2()
        ])

def get_dataloaders(train_csv, val_csv, img_dir, batch_size=32, num_workers=4, img_size=224):
    train_dataset = DeepfakeDataset(train_csv, img_dir, transform=get_transforms(img_size, is_train=True))
    val_dataset = DeepfakeDataset(val_csv, img_dir, transform=get_transforms(img_size, is_train=False))

    persistent_workers = True if num_workers > 0 else False

    train_loader = DataLoader(
        train_dataset, 
        batch_size=batch_size, 
        shuffle=True, 
        num_workers=num_workers,
        pin_memory=True,
        persistent_workers=persistent_workers
    )
    
    val_loader = DataLoader(
        val_dataset, 
        batch_size=batch_size, 
        shuffle=False, 
        num_workers=num_workers,
        pin_memory=True,
        persistent_workers=persistent_workers
    )

    return train_loader, val_loader
