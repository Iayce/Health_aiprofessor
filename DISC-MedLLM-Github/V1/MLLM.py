import torch
import os
from transformers import  AutoModelForCausalLM,AutoTokenizer
from transformers.generation.utils import GenerationConfig
# Use a pipeline as a high-level helper
from transformers import pipeline
# from healthcare_professinal.py import medicalrecord

#pipe = pipeline("text-generation", model="Flmc/DISC-MedLLM", trust_remote_code=True)
model_path = "/root/autodl-tmp/DISC"
class DiscMedlLLM:
    def __init__(self):
        self.model,self.tokenizer = self.init_model()
        #store message
        self.messages = []
        

    def init_model(self):
        print("init...,cuda available: ",torch.cuda.is_available())
        if torch.cuda.is_available():
            print('cuda available!')
          #  torch.set_default_tensor_type(torch.cuda.HalfTensor)
        tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            use_fast=False,
            trust_remote_code=True
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True,
            # mirror='tuna'
        )
        model.generation_config = GenerationConfig.from_pretrained(
            model_path
        )
        return model,tokenizer

    def mchat(self, prompt):
        print("prompt:",prompt)
        model = self.model
        tokenizer = self.tokenizer
        messages = []
        # messages = self.messages
        messages.append({"role":"system","content":"你叫医问灵通，是一个能被调用的专业医疗知识问答插件，现在你将根据传入的医药知识问题、病历等信息生成回复"})
        messages.append({"role": "user", "content": prompt})
        print("messages:",messages)
        
        response = model.chat(tokenizer, messages)
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
        # log the response
        print("response:",response)
        # messages.append({"role": "assitant", "content": response})
        
        return response

def main():
    MLLM = DiscMedlLLM()
    print(MLLM.mchat("你好"))
        # prompt.append({"role": "assistant", "content": response})

if __name__ == '__main__':
    main()
