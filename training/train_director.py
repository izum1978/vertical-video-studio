"""Дообучение режиссёра (Qwen2.5-7B-Instruct, QLoRA, Unsloth) + экспорт в GGUF для Ollama.

Отличия от train_both_models.py:
  * loss считается только на ответе ассистента (train_on_responses_only);
  * есть валидационная выборка, лучший чекпоинт сохраняется;
  * число эпох вместо фиксированных 120 шагов;
  * параметры SFTConfig/SFTTrainer подбираются по сигнатуре установленных версий trl/transformers;
  * в конце экспорт GGUF и готовый Modelfile с num_ctx.

Запуск: python training/train_director.py --epochs 3
(НЕ запускался в песочнице: нужна GPU. Проверен только синтаксис.)
"""
import argparse
import inspect
import json
from pathlib import Path

HERE = Path(__file__).parent


def load_jsonl(path):
    rows = [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]
    return [{"messages": r["messages"]} for r in rows]   # meta обучению не нужна


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="unsloth/Qwen2.5-7B-Instruct-bnb-4bit")
    ap.add_argument("--train", default=str(HERE / "data" / "director_train.jsonl"))
    ap.add_argument("--val", default=str(HERE / "data" / "director_val.jsonl"))
    ap.add_argument("--out", default=str(HERE / "out_director"))
    ap.add_argument("--epochs", type=float, default=3)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--max-len", type=int, default=4096)
    ap.add_argument("--rank", type=int, default=16)
    ap.add_argument("--tag", default="qwen2.5-director-v1")
    a = ap.parse_args()

    from unsloth import FastLanguageModel
    from unsloth.chat_templates import train_on_responses_only
    from datasets import Dataset
    from trl import SFTConfig, SFTTrainer
    import torch

    model, tok = FastLanguageModel.from_pretrained(a.model, max_seq_length=a.max_len, load_in_4bit=True, dtype=None)
    model = FastLanguageModel.get_peft_model(
        model, r=a.rank, lora_alpha=a.rank * 2, lora_dropout=0, bias="none",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        use_gradient_checkpointing="unsloth", random_state=42)

    def to_text(rows):
        return Dataset.from_list([{"text": tok.apply_chat_template(r["messages"], tokenize=False,
                                                                   add_generation_prompt=False)} for r in rows])
    train_rows, val_rows = load_jsonl(a.train), load_jsonl(a.val)
    train_ds, val_ds = to_text(train_rows), to_text(val_rows)

    # Проверка длины: примеры длиннее max-len обрежутся, и модель не увидит конец JSON
    lens = [len(tok(t["text"]).input_ids) for t in train_ds]
    too_long = sum(l > a.max_len for l in lens)
    print(f"Токенов в примере: макс {max(lens)}, средне {sum(lens)//len(lens)}; длиннее {a.max_len}: {too_long}")
    if too_long:
        raise SystemExit("Есть примеры длиннее max-len: увеличьте --max-len или отфильтруйте датасет.")

    cfg_params = inspect.signature(SFTConfig.__init__).parameters
    cfg = dict(
        output_dir=a.out, dataset_text_field="text", per_device_train_batch_size=2,
        gradient_accumulation_steps=4, num_train_epochs=a.epochs, learning_rate=a.lr,
        warmup_ratio=0.05, lr_scheduler_type="cosine", weight_decay=0.01, optim="adamw_8bit",
        logging_steps=5, save_strategy="steps", save_steps=20, eval_steps=20, save_total_limit=2,
        load_best_model_at_end=True, metric_for_best_model="eval_loss", greater_is_better=False,
        bf16=torch.cuda.is_bf16_supported(), fp16=not torch.cuda.is_bf16_supported(),
        seed=42, report_to="none", packing=False)
    cfg["max_seq_length" if "max_seq_length" in cfg_params else "max_length"] = a.max_len
    cfg["eval_strategy" if "eval_strategy" in cfg_params else "evaluation_strategy"] = "steps"

    tr_params = inspect.signature(SFTTrainer.__init__).parameters
    tok_key = "processing_class" if "processing_class" in tr_params else "tokenizer"
    trainer = SFTTrainer(model=model, train_dataset=train_ds, eval_dataset=val_ds,
                         args=SFTConfig(**cfg), **{tok_key: tok})
    trainer = train_on_responses_only(trainer, instruction_part="<|im_start|>user\n",
                                      response_part="<|im_start|>assistant\n")
    trainer.train()

    model.save_pretrained(f"{a.out}/lora")
    tok.save_pretrained(f"{a.out}/lora")
    model.save_pretrained_gguf(f"{a.out}/gguf", tok, quantization_method="q4_k_m")
    gguf = next(Path(a.out, "gguf").glob("*.gguf"))
    modelfile = Path(a.out) / "Modelfile"
    modelfile.write_text(
        f"FROM ./gguf/{gguf.name}\n"
        "PARAMETER num_ctx 8192\nPARAMETER temperature 0.3\nPARAMETER top_p 0.9\n"
        'PARAMETER stop "<|im_end|>"\nPARAMETER stop "<|endoftext|>"\n'
        'TEMPLATE """{{ if .System }}<|im_start|>system\n{{ .System }}<|im_end|>\n{{ end }}'
        '{{ if .Prompt }}<|im_start|>user\n{{ .Prompt }}<|im_end|>\n<|im_start|>assistant\n{{ end }}'
        '{{ .Response }}<|im_end|>"""\n', encoding="utf-8")
    print(f"\nГотово. Подключите модель в Ollama:\n  cd {a.out}\n  ollama create {a.tag} -f Modelfile\n"
          f"и пропишите в .env:  OLLAMA_DIRECTOR_MODEL={a.tag}")


if __name__ == "__main__":
    main()
