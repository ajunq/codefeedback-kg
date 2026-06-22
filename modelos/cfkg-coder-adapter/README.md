---
base_model: Qwen/Qwen2.5-Coder-7B-Instruct
library_name: peft
model_name: cfkg-coder-adapter
tags:
- base_model:adapter:Qwen/Qwen2.5-Coder-7B-Instruct
- lora
- qlora
- sft
- transformers
- trl
license: apache-2.0
pipeline_tag: text-generation
---

# Model Card for cfkg-coder-adapter

**CFKG-Coder-Adapter-v1** is a QLoRA (4-bit NF4) LoRA adapter over
[Qwen/Qwen2.5-Coder-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct)
that specialises the base model to produce structured, Spanish, formative feedback on
introductory-Python student code. It was trained with [TRL](https://github.com/huggingface/trl)
(`SFTTrainer`) as part of **CodeFeedback-KG**.

The adapter is **not a standalone model**: it must be loaded on top of its base model.

## Quick start

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

BASE = "Qwen/Qwen2.5-Coder-7B-Instruct"
ADAPTER = "."  # ruta local a este directorio (o el repo del adaptador)

tokenizer = AutoTokenizer.from_pretrained(BASE)
base = AutoModelForCausalLM.from_pretrained(
    BASE, torch_dtype=torch.bfloat16, device_map="auto"
)
model = PeftModel.from_pretrained(base, ADAPTER)
model.eval()

sistema = (
    "Eres un tutor de programación en Python. Da retroalimentación formativa en "
    "español con cinco partes: tipo de error, concepto implicado, explicación "
    "divulgativa, explicación técnica y sugerencia de mejora."
)
codigo = (
    "def media(numeros):\n"
    "    total = 0\n"
    "    for n in numeros:\n"
    "        total += n\n"
    "    return total / len(numeros)\n"
    "\n"
    "print(media([]))"
)
usuario = (
    "Revisa este código de un estudiante y explica qué falla.\n\n"
    "Código:\n" + codigo
)

mensajes = [
    {"role": "system", "content": sistema},
    {"role": "user", "content": usuario},
]
input_ids = tokenizer.apply_chat_template(
    mensajes, add_generation_prompt=True, return_tensors="pt"
).to(model.device)
generado = model.generate(input_ids, max_new_tokens=512, do_sample=False)
respuesta = tokenizer.decode(generado[0, input_ids.shape[-1]:], skip_special_tokens=True)
print(respuesta)
```

The example code raises `ZeroDivisionError` when the list is empty: the adapter is trained to
name the error type, link it to the underlying Python concept and suggest a guard clause, all in
Spanish and following the five-part diagnosis above.

## Training procedure

QLoRA — 4-bit NF4 quantisation of the base model plus LoRA low-rank update matrices, with NEFTune
during instruction tuning — trained with TRL's `SFTTrainer` on the CodeFeedback-KG Spanish
code-feedback dataset, with a fixed random seed (**11**) on a single NVIDIA RTX 5090 (32 GB),
Python 3.12. LoRA configuration (from `adapter_config.json`): rank `r=16`, `lora_alpha=32`,
`lora_dropout=0.1`, `task_type=CAUSAL_LM`, target modules
`q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj`.

Training data, evaluation (in- and out-of-distribution), intended use, limitations and the full
provenance are documented in **[`MODEL-CARD.md`](./MODEL-CARD.md)**, the source of truth for this
adapter.

### Framework versions

- PEFT 0.19.1
- TRL 1.6.0
- Transformers 5.12.1
- PyTorch 2.11.0+cu128
- Datasets 5.0.0
- Tokenizers 0.22.2

## License and citations

Apache-2.0 — see [`LICENSE`](./LICENSE) and [`NOTICE`](./NOTICE). The base model
Qwen2.5-Coder-7B-Instruct is © Alibaba Cloud / Qwen Team and is also licensed under Apache-2.0.
Cite CodeFeedback-KG (repository `CITATION.cff`), the base model, and TRL:

```bibtex
@software{vonwerra2020trl,
  title   = {{TRL: Transformers Reinforcement Learning}},
  author  = {von Werra, Leandro and Belkada, Younes and Tunstall, Lewis and Beeching, Edward and Thrush, Tristan and Lambert, Nathan and Huang, Shengyi and Rasul, Kashif and Gallouédec, Quentin},
  license = {Apache-2.0},
  url     = {https://github.com/huggingface/trl},
  year    = {2020}
}
```
