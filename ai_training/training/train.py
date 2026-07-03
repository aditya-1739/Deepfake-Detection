import os
import yaml
import argparse
from pathlib import Path
import pytorch_lightning as pl
from data.dataset import get_dataloaders
from pytorch_lightning.loggers import CSVLogger, TensorBoardLogger
from pytorch_lightning.callbacks import ModelCheckpoint, EarlyStopping, LearningRateMonitor
import datetime
from training.lightning_module import DeepfakeLightningModule

def train():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="config/training.yaml")
    parser.add_argument("--model_config", type=str, default="config/model.yaml")
    parser.add_argument("--dataset_config", type=str, default="config/dataset.yaml")
    args = parser.parse_args()

    # Handle path differences when running from project root vs ai_training dir
    base_dir = Path("ai_training") if Path("ai_training").exists() else Path(".")
    config_path = base_dir / args.config
    model_config_path = base_dir / args.model_config
    dataset_config_path = base_dir / args.dataset_config

    with open(config_path, 'r') as f:
        train_cfg = yaml.safe_load(f)
    with open(model_config_path, 'r') as f:
        model_cfg = yaml.safe_load(f)
    with open(dataset_config_path, 'r') as f:
        data_cfg = yaml.safe_load(f)

    pl.seed_everything(train_cfg.get('seed', 42), workers=True)

    # Production Training (Milestone 3)
    experiment_id = "experiment_002"
    
    exp_root = Path("experiments") if Path("experiments").exists() else Path("../../experiments")
    exp_dir = exp_root / experiment_id
    os.makedirs(exp_dir, exist_ok=True)

    csv_logger = CSVLogger(save_dir=str(exp_root), name=experiment_id)
    tb_logger = TensorBoardLogger(save_dir=str(exp_root), name=experiment_id, version="tensorboard")
    loggers = [csv_logger, tb_logger]

    model = DeepfakeLightningModule(
        model_name=model_cfg['model_name'],
        learning_rate=train_cfg['learning_rate'],
        weight_decay=train_cfg['weight_decay'],
        num_classes=model_cfg['num_classes']
    )

    checkpoint_callback = ModelCheckpoint(
        dirpath=os.path.join(exp_dir, 'checkpoints'),
        filename='best',
        save_top_k=1,
        verbose=True,
        monitor='val_loss',
        mode='min'
    )
    last_checkpoint_callback = ModelCheckpoint(
        dirpath=os.path.join(exp_dir, 'checkpoints'),
        filename='last',
        save_last=True,
    )
    lr_monitor = LearningRateMonitor(logging_interval='epoch')
    early_stop_callback = EarlyStopping(
        monitor='val_loss',
        patience=train_cfg['patience'],
        verbose=True,
        mode='min'
    )

    import torch
    
    cuda_available = torch.cuda.is_available()
    if cuda_available:
        print(f"CUDA Available: True")
        print(f"GPU Name: {torch.cuda.get_device_name(0)}")
        print(f"CUDA Version: {torch.version.cuda}")
        print(f"PyTorch Version: {torch.__version__}")
        total_mem = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"Total GPU Memory: {total_mem:.2f} GB")
        accelerator = "gpu"
    else:
        print("WARNING: CUDA is not available. Falling back to CPU execution. GPU acceleration is unavailable.")
        accelerator = "cpu"

    trainer = pl.Trainer(
        logger=loggers,
        callbacks=[checkpoint_callback, last_checkpoint_callback, early_stop_callback, lr_monitor],
        max_epochs=train_cfg['epochs'],
        precision="16-mixed" if train_cfg.get('mixed_precision', False) and cuda_available else 32,
        accelerator=accelerator,
        devices=1 if accelerator == "gpu" else "auto",
        log_every_n_steps=10
    )

    # Get Paths based on where script is executed
    project_root = Path(".") if Path("datasets").exists() else Path("../../")
    train_csv = project_root / data_cfg['train_csv']
    val_csv = project_root / data_cfg['val_csv']
    img_dir = project_root / data_cfg['processed_dir']

    import multiprocessing
    num_workers = min(os.cpu_count() or 4, 8) if cuda_available else 0

    train_loader, val_loader = get_dataloaders(
        train_csv=str(train_csv),
        val_csv=str(val_csv),
        img_dir=str(img_dir),
        batch_size=train_cfg['batch_size'],
        num_workers=num_workers,
        img_size=data_cfg['image_size']
    )
    
    print(f"Training pipeline configured for {model_cfg['model_name']} under {experiment_id}")
    trainer.fit(model, train_loader, val_loader)

if __name__ == "__main__":
    train()
