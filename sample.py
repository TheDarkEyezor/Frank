# import requests
# import torch
# from PIL import Image
# from transformers import MllamaForConditionalGeneration, AutoProcessor, TextIteratorStreamer
# from threading import Thread
# import bitsandbytes

# model_id = "meta-llama/Llama-3.2-11B-Vision-Instruct"

# # quantization_config = bitsandbytes.BitsAndBytesConfig(
# #     load_in_4bit=True,
# #     bnb_4bit_compute_dtype=torch.bfloat16,
# #     bnb_4bit_quant_type="nf4",
# # )

# model = MllamaForConditionalGeneration.from_pretrained(
#     model_id,
#     torch_dtype=torch.float16,
#     device_map="auto",
#     # offload_folder="offload",
#     # low_cpu_mem_usage=True,
# )
# processor = AutoProcessor.from_pretrained(model_id)

# # url = "https://huggingface.co/datasets/huggingface/documentation-images/resolve/0052a70beed5bf71b92610a43a52df6d286cd5f3/diffusers/rabbit.jpg"
# # image = Image.open(requests.get(url, stream=True).raw)

# # Replace with path to your local image file
# image_path = "test.png"  
# image = Image.open(image_path)

# messages = [
#     {"role": "user", "content": [
#         {"type": "image"},
#         {"type": "text", "text": "If I had to write a haiku for this one, it would be: "}
#     ]}
# ]
# input_text = processor.apply_chat_template(messages, add_generation_prompt=True)
# inputs = processor(
#     image,
#     input_text,
#     add_special_tokens=False,
#     return_tensors="pt"
# ).to(model.device)

# # Create a streamer
# streamer = TextIteratorStreamer(processor.tokenizer, skip_prompt=True)

# # Generate in a separate thread
# generation_kwargs = dict(
#     **inputs,
#     max_new_tokens=30,
#     streamer=streamer
# )
# thread = Thread(target=model.generate, kwargs=generation_kwargs)
# thread.start()

# # Print tokens as they're generated
# print("Generating: ", end="", flush=True)
# for token in streamer:
#     print(token, end="", flush=True)
# print("\nGeneration complete!")


# ------------------ accessing terminal
