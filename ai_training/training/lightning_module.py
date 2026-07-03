import pytorch_lightning as pl
import torch
import torch.nn as nn
import torch.optim as optim
from torchmetrics import Accuracy, F1Score, AUROC, Precision, Recall
import timm

class DeepfakeLightningModule(pl.LightningModule):
    def __init__(self, model_name: str, learning_rate: float, weight_decay: float, num_classes: int = 2):
        super().__init__()
        self.save_hyperparameters()
        
        self.model = timm.create_model(model_name, pretrained=True, num_classes=num_classes)
        self.criterion = nn.CrossEntropyLoss()
        
        self.train_acc = Accuracy(task="multiclass", num_classes=num_classes)
        self.val_acc = Accuracy(task="multiclass", num_classes=num_classes)
        self.val_f1 = F1Score(task="multiclass", num_classes=num_classes)
        self.val_auroc = AUROC(task="multiclass", num_classes=num_classes)
        self.val_prec = Precision(task="multiclass", num_classes=num_classes)
        self.val_rec = Recall(task="multiclass", num_classes=num_classes)

    def forward(self, x):
        return self.model(x)

    def training_step(self, batch, batch_idx):
        x, y = batch
        logits = self(x)
        loss = self.criterion(logits, y)
        preds = torch.argmax(logits, dim=1)
        
        self.train_acc(preds, y)
        self.log('train_loss', loss, on_step=True, on_epoch=True, prog_bar=True)
        self.log('train_acc', self.train_acc, on_step=False, on_epoch=True, prog_bar=True)
        return loss

    def validation_step(self, batch, batch_idx):
        x, y = batch
        logits = self(x)
        loss = self.criterion(logits, y)
        preds = torch.argmax(logits, dim=1)
        probs = torch.softmax(logits, dim=1)
        
        self.val_acc(preds, y)
        self.val_f1(preds, y)
        self.val_auroc(probs, y)
        self.val_prec(preds, y)
        self.val_rec(preds, y)
        
        self.log('val_loss', loss, on_epoch=True, prog_bar=True)
        self.log('val_acc', self.val_acc, on_epoch=True, prog_bar=True)
        self.log('val_f1', self.val_f1, on_epoch=True, prog_bar=True)
        self.log('val_auroc', self.val_auroc, on_epoch=True)
        self.log('val_prec', self.val_prec, on_epoch=True, prog_bar=True)
        self.log('val_rec', self.val_rec, on_epoch=True, prog_bar=True)

    def configure_optimizers(self):
        optimizer = optim.AdamW(self.parameters(), lr=self.hparams.learning_rate, weight_decay=self.hparams.weight_decay)
        scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=10) # T_max can be dynamic
        return [optimizer], [scheduler]
