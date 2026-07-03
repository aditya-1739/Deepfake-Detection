import os
import argparse
import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, precision_recall_curve

from data.dataset import get_dataloaders
from models.factory import create_model

def evaluate_model(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Evaluating on device: {device}")

    # Data Loader (Using val/test set)
    _, test_loader = get_dataloaders(
        args.test_csv, args.test_csv, args.img_dir, 
        batch_size=args.batch_size, num_workers=args.num_workers
    )

    # Load Model
    model = create_model(args.model_name, num_classes=2, pretrained=False)
    model.load_state_dict(torch.load(args.checkpoint_path, map_location=device))
    model.to(device)
    model.eval()

    all_preds = []
    all_probs = []
    all_labels = []

    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(device)
            outputs = model(inputs)
            probs = torch.softmax(outputs, dim=1)[:, 1].cpu().numpy()
            preds = np.argmax(outputs.cpu().numpy(), axis=1)
            
            all_probs.extend(probs)
            all_preds.extend(preds)
            all_labels.extend(labels.numpy())

    all_labels = np.array(all_labels)
    all_preds = np.array(all_preds)
    all_probs = np.array(all_probs)

    # Metrics
    acc = accuracy_score(all_labels, all_preds)
    prec = precision_score(all_labels, all_preds)
    rec = recall_score(all_labels, all_preds)
    f1 = f1_score(all_labels, all_preds)
    try:
        roc_auc = roc_auc_score(all_labels, all_probs)
    except ValueError:
        roc_auc = float('nan') # In case of single class in test batch

    cm = confusion_matrix(all_labels, all_preds)

    print("\n--- Evaluation Results ---")
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1-Score:  {f1:.4f}")
    print(f"ROC-AUC:   {roc_auc:.4f}")

    os.makedirs(args.output_dir, exist_ok=True)

    # Confusion Matrix Plot
    plt.figure(figsize=(6,5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Real', 'Fake'], yticklabels=['Real', 'Fake'])
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title(f'Confusion Matrix - {args.model_name}')
    plt.savefig(os.path.join(args.output_dir, f'cm_{args.model_name}.png'))
    plt.close()

    # Precision-Recall Curve Plot
    precision_curve, recall_curve, _ = precision_recall_curve(all_labels, all_probs)
    plt.figure(figsize=(6,5))
    plt.plot(recall_curve, precision_curve, marker='.')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title(f'Precision-Recall Curve - {args.model_name}')
    plt.savefig(os.path.join(args.output_dir, f'pr_{args.model_name}.png'))
    plt.close()

    print(f"Saved evaluation plots to {args.output_dir}/")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, required=True, help="Timm backbone name")
    parser.add_argument("--checkpoint_path", type=str, required=True, help="Path to .pth file")
    parser.add_argument("--test_csv", type=str, required=True, help="Path to test metadata CSV")
    parser.add_argument("--img_dir", type=str, required=True, help="Path to processed images")
    parser.add_argument("--output_dir", type=str, default="evaluation_results")
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--num_workers", type=int, default=4)
    
    args = parser.parse_args()
    evaluate_model(args)
