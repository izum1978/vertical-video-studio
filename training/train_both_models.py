"""Скрипт двойного LoRA дообучения Qwen 2.5:

1. Режиссёр и Сценарист (Qwen 2.5 7B) — по датасету вирусных шортсов (dataset_viral_shorts.jsonl).
2. Оператор и Постановщик (Qwen 2.5-Coder 7B) — по датасету визуальной непрерывности и раскадровки (dataset_cinematographer.jsonl).

Запуск:
python train_both_models.py --target all
python train_both_models.py --target director
python train_both_models.py --target cinematographer
"""
import argparse
import sys
from pathlib import Path

TRAINING_DIR = Path(__file__).parent
DATASETS = {
    "director": {
        "model_name": "unsloth/Qwen2.5-7B-Instruct-bnb-4bit",
        "dataset_path": TRAINING_DIR / "dataset_viral_shorts.jsonl",
        "output_dir": TRAINING_DIR / "lora_qwen_director",
        "ollama_tag": "qwen2.5-director:7b",
        "desc": "Сценарист и Режиссёр вирусных шортсов",
    },
    "cinematographer": {
        "model_name": "unsloth/Qwen2.5-Coder-7B-Instruct-bnb-4bit",
        "dataset_path": TRAINING_DIR / "dataset_cinematographer.jsonl",
        "output_dir": TRAINING_DIR / "lora_qwen_cinematographer",
        "ollama_tag": "qwen2.5-cinematographer:7b",
        "desc": "Оператор-постановщик визуальной непрерывности и ракурсов",
    },
}


def train_single_model(target_key: str):
    info = DATASETS[target_key]
    print(f"\n{'='*70}")
    print(f"🎬 НАЧАЛО ДООБУЧЕНИЯ: {info['desc']}")
    print(f"Базовая модель: {info['model_name']}")
    print(f"Датасет: {info['dataset_path'].name}")
    print(f"Папка сохранения: {info['output_dir']}")
    print(f"{'='*70}\n")

    try:
        from unsloth import FastLanguageModel
        import torch
        from trl import SFTTrainer
        from transformers import TrainingArguments
        from datasets import load_dataset
    except ImportError:
        print(
            "\n[!] Необходимые ML-библиотеки не установлены в текущем окружении.\n"
            "Для локального обучения установите:\n"
            "pip install unsloth torch torchvision torchaudio trl transformers datasets\n"
            "Или запустите обучение в бесплатном Google Colab с GPU T4.\n"
        )
        return False

    max_seq_length = 2048

    print("--> 1/5 Загружаем 4-bit квантованную базовую модель...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=info["model_name"],
        max_seq_length=max_seq_length,
        dtype=None,
        load_in_4bit=True,
    )

    print("--> 2/5 Добавляем LoRA адаптеры (Q, K, V, O, Gate, Up, Down)...")
    model = FastLanguageModel.get_peft_model(
        model,
        r=16,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_alpha=32,
        lora_dropout=0,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=42,
    )

    print(f"--> 3/5 Загружаем и форматируем датасет {info['dataset_path']}...")
    dataset = load_dataset("json", data_files=str(info["dataset_path"]), split="train")

    def format_prompts(batch):
        conversations = batch["messages"]
        texts = [tokenizer.apply_chat_template(conv, tokenize=False, add_generation_prompt=False) for conv in conversations]
        return {"text": texts}

    dataset = dataset.map(format_prompts, batched=True)

    print("--> 4/5 Обучение LoRA...")
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=max_seq_length,
        dataset_num_proc=2,
        packing=False,
        args=TrainingArguments(
            per_device_train_batch_size=2,
            gradient_accumulation_steps=4,
            warmup_steps=10,
            max_steps=120,
            learning_rate=2e-4,
            fp16=not torch.cuda.is_bf16_supported(),
            bf16=torch.cuda.is_bf16_supported(),
            logging_steps=10,
            optim="adamw_8bit",
            weight_decay=0.01,
            lr_scheduler_type="cosine",
            seed=42,
            output_dir=str(info["output_dir"]),
            report_to="none",
        ),
    )

    trainer.train()

    print(f"--> 5/5 Сохранение LoRA весов в {info['output_dir']}...")
    model.save_pretrained(str(info["output_dir"]))
    tokenizer.save_pretrained(str(info["output_dir"]))

    print(f"\n✅ Дообучение {info['desc']} успешно завершено!\n")
    return True


def main():
    parser = argparse.ArgumentParser(description="LoRA дообучение дуэта Qwen (Режиссёр + Оператор)")
    parser.add_argument(
        "--target",
        choices=["all", "director", "cinematographer"],
        default="all",
        help="Какую модель обучать: director, cinematographer или all",
    )
    args = parser.parse_args()

    targets = ["director", "cinematographer"] if args.target == "all" else [args.target]

    for t in targets:
        success = train_single_model(t)
        if not success:
            sys.exit(1)


if __name__ == "__main__":
    main()
