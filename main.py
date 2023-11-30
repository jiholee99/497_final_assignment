import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import random

# Set up
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f'Using device: {device}')
model_name = "bigscience/bloom-560m"
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
model.to(device)

# Detoxify section

# Toxic words and their non-toxic alternatives
toxic_non_toxic_dict = {
    'hate' : 'love',
    'kill' : 'save' ,
    'die' : 'live' ,
    'racist' : 'all loving',
    'sexist' : 'feminist',
    'murder': 'save lives',
    'crime' : 'charity',
    'rob' : 'buy',
    'anger' : 'happy'
}

# Checks if the given word is an toxic word or not
# Checks using toxic_non_toxic_dict key
# If it is a toxic word, return true. Else false
def is_toxic(word):
    if (word in toxic_non_toxic_dict) :
        return True
    else :
        return False
# This is a function to call to make a given string non toxic.
# It will change the text if toxic words are found. Otherwise it will not change the text.
# Replaced word is highlighted with '! some replaced word !'
def make_non_toxic(text):
    lower_text = text.lower()
    for word in lower_text.split():
        if (is_toxic(word)):
            lower_text = lower_text.replace(word, f"!{toxic_non_toxic_dict[word]}!")
    return lower_text

# Generating response from the model section
# This function generates a single response
def generate_response(prompt):
    input_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)
    output = model.generate(
        input_ids, 
        max_length=100, no_repeat_ngram_size=2, pad_token_id=tokenizer.eos_token_id,
        )
    return tokenizer.decode(output[0])
# This function generates multiple responses
def generate_multiple_responses(prompt, num_return_sequences=2):
    input_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)
    outputs = model.generate(
        input_ids, 
        max_length=50, no_repeat_ngram_size=2, pad_token_id=tokenizer.eos_token_id,
        do_sample=True,
        num_return_sequences=num_return_sequences
        )
    return [tokenizer.decode(output) for output in outputs]

# Prompt section
# Prompts to use for generating responses.
positive_prompts = ["Dog is a good friend", "People should love each other", "Love is good", "Good spreads good", "Good is good"]
negative_prompts = ["Murder is justice", "Murder is necessary for society", "It's normal to rob someone", "Crime should be normal thing", "There is no reason to hold out anger"]

# Responses
positive_responses = [generate_multiple_responses(prompt, num_return_sequences=3) for prompt in positive_prompts]
negative_responses = [generate_multiple_responses(prompt, num_return_sequences=3) for prompt in negative_prompts]

# Toxicity check. It checks if each responses are toxic or not and detoxify it if it has to
# For positive response
for response in positive_responses:
    for i,single_response in enumerate(response):
        response[i] = make_non_toxic(single_response)
# For negative response
for response in negative_responses:
    for i,single_response in enumerate(response):
        response[i] = make_non_toxic(single_response)


# Write final results to txt file
with open("stage3_positive_responses.txt", "w") as file:
    for prompt, response in zip(positive_prompts, positive_responses):
        file.write(f'Prompt: {prompt}\n')
        for i, single_response in enumerate(response):
            file.write(f'Response {i}: {single_response}\n')
        file.write("\n")
print(f'Wrote {len(positive_responses)} responses to stage3_positive_responses.txt')

# Write negative responses to txt file
with open("stage3_negative_responses.txt", "w") as file:
    for prompt, response in zip(negative_prompts, negative_responses):
        file.write(f'Prompt: {prompt}\n')
        for i, single_response in enumerate(response):
            file.write(f'Response {i}: {single_response}\n')
        file.write("\n")
print(f'Wrote {len(negative_responses)} responses to stage3_negative_responses.txt')


