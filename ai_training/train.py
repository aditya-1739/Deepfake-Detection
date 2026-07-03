import os
import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from data.dataset import get_dataloaders
from models.factory import create_model

def train_model(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Data Loaders
    train_loader, val_loader = get_dataloaders(
        args.train_csv, args.val_csv, args.img_dir, 
        batch_size=args.batch_size, num_workers=args.num_workers
    )

    # Model Factory
    model = create_model(args.model_name, num_classes=2, pretrained=True)
    model = model.to(device)

    # Loss and Optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)

    # Early stopping tracking
    best_val_loss = float('inf')
    patience_counter = 0

    os.makedirs(args.save_dir, exist_ok=True)

    for epoch in range(args.epochs):
        # Training Phase
        model.train()
        train_loss = 0.0
        correct = 0
        total = 0
        
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item() * inputs.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
        train_loss = train_loss / total
        train_acc = 100. * correct / total
        
        # Validation Phase
        model.eval()
        val_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item() * inputs.size(0)
                _, predicted = outputs.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()
                
        val_loss = val_loss / total
        val_acc = 100. * correct / total
        
        scheduler.step()

        print(f"Epoch {epoch+1}/{args.epochs} - "
              f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}% - "
              f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")

        # Early Stopping and Checkpointing
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            save_path = os.path.join(args.save_dir, f"best_{args.model_name}.pth")
            torch.save(model.state_dict(), save_path)
            print(f"--> Saved best model checkpoint to {save_path}")
        else:
            patience_counter += 1
            if patience_counter >= args.patience:
                print("Early stopping triggered.")
                break

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, default="resnet50", help="Timm backbone name")
    parser.add_argument("--train_csv", type=str, required=True, help="Path to train metadata CSV")
    parser.add_argument("--val_csv", type=str, required=True, help="Path to val metadata CSV")
    parser.add_argument("--img_dir", type=str, required=True, help="Path to processed images")
    parser.add_argument("--save_dir", type=str, default="checkpoints")
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--num_workers", type=int, default=4)
    parser.add_argument("--patience", type=int, default=5, help="Early stopping patience")
    
    args = parser.parse_args()
    train_model(args)
