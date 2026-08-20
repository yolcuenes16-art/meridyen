"""LoRA multi-task trainer. Dataset rows: text, sentiment, toxicity, spam, focus_fit, learning_fit, fun_fit."""
from __future__ import annotations

import argparse
from pathlib import Path


def train(dataset_path: str, base_model: str, output_dir: str) -> None:
    from datasets import load_dataset
    from peft import LoraConfig, TaskType, get_peft_model
    from transformers import AutoModelForSequenceClassification, AutoTokenizer, TrainingArguments, Trainer

    labels = ["sentiment", "toxicity", "spam", "focus_fit", "learning_fit", "fun_fit"]
    data = load_dataset("json", data_files={"train": dataset_path})["train"]
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    def tokenize(row):
        encoded = tokenizer(row["text"], truncation=True, max_length=256)
        encoded["labels"] = [float(row[name]) for name in labels]
        return encoded
    tokenized = data.map(tokenize, remove_columns=data.column_names)
    model = AutoModelForSequenceClassification.from_pretrained(base_model, num_labels=len(labels), problem_type="multi_label_regression")
    model = get_peft_model(model, LoraConfig(task_type=TaskType.SEQ_CLS, r=16, lora_alpha=32, lora_dropout=.05, target_modules=["query", "value"]))
    trainer = Trainer(model=model, args=TrainingArguments(output_dir=output_dir, learning_rate=2e-4, num_train_epochs=3,
        per_device_train_batch_size=8, save_strategy="epoch", logging_strategy="steps", logging_steps=10), train_dataset=tokenized)
    trainer.train(); trainer.save_model(output_dir); tokenizer.save_pretrained(output_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("dataset"); parser.add_argument("--base-model", default="dbmdz/bert-base-turkish-cased"); parser.add_argument("--output", default="artifacts/lora")
    args = parser.parse_args(); Path(args.output).mkdir(parents=True, exist_ok=True); train(args.dataset, args.base_model, args.output)
