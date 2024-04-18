#!/usr/bin/env python
import os
import random
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
#from superprompter.download_models import download_models
import modules.config as top_config

global tokenizer, model
script_dir = os.path.dirname(os.path.abspath(__file__))  # Script directory
#modelDir = os.path.join(script_dir, "./model_files/" )
modelDir = os.path.join(top_config.path_llms, "superprompt-v1" )

def load_models():
 
    if not all(os.path.exists(os.path.join(modelDir, "model.safetensors")) for file in modelDir):
        top_config.downloading_superprompter_model()
        print("[SuperPrompt] Downloaded the model file for superprompter. \n")
        #download_models()
    # else:
        # print("Model files found. Skipping download.\n")

    # print("Loading SuperPrompt-v1 model...\n")


    global tokenizer, model
    tokenizer = T5Tokenizer.from_pretrained(modelDir)
    model = T5ForConditionalGeneration.from_pretrained(modelDir, torch_dtype=torch.float16)

    # print("SuperPrompt-v1 model loaded successfully.\n")

def unload_models():
    global tokenizer, model
    del tokenizer
    del model

    for file in os.listdir(modelDir):
        os.remove(os.path.join(modelDir, file))
    os.rmdir(modelDir)



def answer(input_text="", max_new_tokens=512, repetition_penalty=1.2, temperature=0.5, top_p=1, top_k = 1 , seed=-1):
       
    if seed == -1:
        seed = random.randint(1, 1000000)

    torch.manual_seed(seed)

    if torch.cuda.is_available():
        device = 'cuda'
    else:
        device = 'cpu'

    input_ids = tokenizer(input_text, return_tensors="pt").input_ids.to(device)
    if torch.cuda.is_available():
        model.to('cuda')

    print(f'[SuperPrompt] ready to expend: "{input_text}"')

    outputs = model.generate(input_ids, max_new_tokens=max_new_tokens, repetition_penalty=repetition_penalty,
                            do_sample=True, temperature=temperature, top_p=top_p, top_k=top_k)

    dirty_text = tokenizer.decode(outputs[0])
    text = dirty_text.replace("<pad>", "").replace("</s>", "").strip()
    
    return text