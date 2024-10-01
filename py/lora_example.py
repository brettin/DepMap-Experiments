from vllm import LLM, SamplingParams
import ray
from vllm.lora.request import LoRARequest

lora_adapter = "/rbscratch/chia/TMP_adapter_Meta-Llama-3-8B-Instruct_1.0"

llm = LLM(model="meta-llama/Meta-Llama-3-8B-Instruct", enable_lora=True)
sampling_params = SamplingParams(
  temperature=0,
  max_tokens=256,
  stop=["[/assistant]"]
)
prompts = ["What color is the sky?",]
outputs = llm.generate(prompts,sampling_params,lora_request=LoRARequest(
    "sql_adapter",
    1,
    lora_adapter,
    )
)

from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")
generated_output = tokenizer.decode(outputs[0].outputs[0].token_ids,skip_special_tokens=True)
print(generated_output)

