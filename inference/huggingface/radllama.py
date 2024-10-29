# from transformers import AutoModelForCausalLM, AutoTokenizer

# device = "cuda" # the device to load the model onto

# model = AutoModelForCausalLM.from_pretrained("BioMistral/BioMistral-7B")
# tokenizer = AutoTokenizer.from_pretrained("BioMistral/BioMistral-7B")

# messages = [
#     {"role": "user", "content": "Who are you?"},
# ]

# encodeds = tokenizer.apply_chat_template(messages, return_tensors="pt")

# model_inputs = encodeds.to(device)
# model.to(device)

# generated_ids = model.generate(model_inputs, max_new_tokens=1000)
# decoded = tokenizer.batch_decode(generated_ids)
# print(decoded[0])

# # Use a pipeline as a high-level helper
# from transformers import pipeline

# messages = [
#     {"role": "user", "content": "Who are you?"},
# ]
# pipe = pipeline("text-generation", model="BioMistral/BioMistral-7B")
# print(pipe(messages, max_new_tokens=1000))