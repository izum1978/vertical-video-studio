"""
Тест локального инференса SD-Turbo / SDXL-Lightning на RTX 4050.
"""
import time
import torch
from diffusers import AutoPipelineForText2Image

device = "cuda" if torch.cuda.is_available() else "cpu"
dtype = torch.float16 if device == "cuda" else torch.float32

print(f"Device: {device}, Dtype: {dtype}, GPU: {torch.cuda.get_device_name(0) if device=='cuda' else 'CPU'}")

print("Загрузка модели stabilityai/sd-turbo...")
t0 = time.time()
pipe = AutoPipelineForText2Image.from_pretrained(
    "stabilityai/sd-turbo",
    torch_dtype=dtype,
    variant="fp16" if device == "cuda" else None,
)
if device == "cuda":
    pipe.enable_attention_slicing()
    pipe.enable_vae_slicing()
    pipe.to(device)

print(f"Модель загружена за {time.time() - t0:.2f} сек.")

prompt = "2D dark animated cartoon illustration of ballistic missile alert in Kyiv, night city red emergency lights, graphic novel style, vertical 9:16"
print("Генерация тестового кадра...")
t1 = time.time()
with torch.inference_mode():
    img = pipe(prompt=prompt, width=768, height=1344, num_inference_steps=1, guidance_scale=0.0).images[0]

img = img.resize((1080, 1920))
img.save("test_generated_scene.jpg", quality=95)
print(f"Кадр 1080x1920 сгенерирован за {time.time() - t1:.2f} сек! Сохранено в test_generated_scene.jpg")
