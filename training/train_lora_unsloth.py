"""Скрипт быстрого LoRA дообучения Qwen 2.5 на датасете вирусных шортсов с помощью Unsloth.

Работает на любой видеокарте от 8 ГБ VRAM (RTX 3060/4060/4070/4090) или в бесплатном Google Colab T4.
Время обучения: ~15-30 минут на 500-1000 примеров.
"""
import os
from pathlib import Path

# 1. Проверяем зависимости
try:
    from unsloth import FastLanguageModel
    import torch
    from trl import SFTTrainer
    from transformers import TrainingArguments
    from datasets import load_dataset
except ImportError:
    print(
        "\n[!] Библиотека unsloth не установлена.\n"
        "Для запуска установите:\n"
        "pip install unsloth torch torchvision torchaudio trl transformers datasets\n"
        "Либо запустите этот скрипт в Google Colab с GPU T4.\n"
    )
    import sys
    sys.exit(1)

# 2. Параметры модели и обучения
max_seq_length = 2048
dtype = None # Auto detection (Float16 / Bfloat16)
load_in_4bit = True # 4-bit квантование для экономии 70% VRAM

MODEL_NAME = "unsloth/Qwen2.5-7B-Instruct-bnb-4bit" # или unsloth/Qwen2.5-14B-Instruct-bnb-4bit
OUTPUT_DIR = "./lora_viral_qwen"
DATASET_PATH = Path(__file__).parent / "dataset_viral_shorts.jsonl"

print(f"--> Загружаем базовую модель {MODEL_NAME}...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=MODEL_NAME,
    max_seq_length=max_seq_length,
    dtype=dtype,
    load_in_4bit=load_in_4bit,
)

# 3. Настройка LoRA адаптеров
print("--> Добавляем LoRA адаптеры (Q, K, V, O, Gate, Up, Down)...")
model = FastLanguageModel.get_peft_model(
    model,
    r=16, # LoRA Rank (16 или 32 оптимально для структуры сценариев)
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha=32,
    lora_dropout=0, # Unsloth оптимизирован под dropout=0
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=42,
)

# 4. Форматирование датасета под ChatML (стандарт Qwen 2.5)
print(f"--> Загружаем датасет {DATASET_PATH}...")
dataset = load_dataset("json", data_files=str(DATASET_PATH), split="train")

def format_prompts(batch):
    conversations = batch["messages"]
    texts = [tokenizer.apply_chat_template(conv, tokenize=False, add_generation_prompt=False) for conv in conversations]
    return {"text": texts}

dataset = dataset.map(format_prompts, batched=True)

# 5. Обучение
print("--> Начинаем обучение...")
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
        max_steps=120, # для небольшого датасета; увеличьте до 300-500 для 1000 примеров
        learning_rate=2e-4,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=5,
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="cosine",
        seed=42,
        output_dir=OUTPUT_DIR,
        report_to="none",
    ),
)

trainer.train()

# 6. Сохранение LoRA весов
print(f"--> Сохраняем LoRA веса в {OUTPUT_DIR}...")
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

# 7. Экспорт в GGUF для Ollama
GGUF_DIR = "./gguf_output"
print(f"--> Экспортируем в GGUF (q4_k_m) для запуска в Ollama...")
try:
    model.save_pretrained_gguf(GGUF_DIR, tokenizer, quantization_method="q4_k_m")
    print(f"\n[ГОТОВО] Модель экспортирована в {GGUF_DIR}!")
    print("Для добавления в Ollama выполните:")
    print("  ollama create viral-qwen -f training/Modelfile")
except Exception as e:
    print(f"[!] Ошибка экспорта GGUF: {e}. Можно объединить веса вручную.")
