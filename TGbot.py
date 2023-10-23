!pip install pyTelegramBotAPI
!pip install transformers

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

tokenizer = AutoTokenizer.from_pretrained("sberbank-ai/rugpt3large_based_on_gpt2")

model = AutoModelForCausalLM.from_pretrained("sberbank-ai/rugpt3large_based_on_gpt2").cuda()

def generate_text(text, max_letters):
  ids = torch.tensor(tokenizer.encode(text)).unsqueeze(0).cuda()
  generated_ids = model.generate(
                          input_ids=ids,  # Input.
                          max_length=max_letters,  # Default 20.
                          min_length=0,  # Default 0.
                          do_sample=True,  # Don't use greedy decoding.
                          early_stopping=False,  # Search is stopped when at least num_beams sentences finished.
                          temperature=2.45,  # Default 1.0.
                          top_k=45,  # Default 50.
                          top_p=0.7,  # Default 1.0.
                          repetition_penalty=2.0,  # Rep. penalty.
                          num_beams=6,
                          num_return_sequences=1, #  Num ind. computed returned sequences.
                          bos_token_id=tokenizer.bos_token_id
                          )
  result = tokenizer.decode(generated_ids[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)

  return result

import telebot

API_TOKEN = '' # Write your API here.

MAX_LEN = 75

last_generated = ''

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет! Отправляй мне начало историй, а я буду их продолжать :)')
    bot.send_message(message.chat.id, 'Сейчас максимальная длина рассказа - ' + str(MAX_LEN) + ' букв, но ты можешь сделать ее больше командами!')

@bot.message_handler(commands=['increase_len'])
def increase_len(message):
  global MAX_LEN
  if MAX_LEN < 200:
    MAX_LEN += 25
    bot.send_message(message.chat.id, 'Увеличил максимальное количество букв до {}'.format(MAX_LEN))
  else:
    bot.send_message(message.chat.id, 'Уже и так много :(')

@bot.message_handler(commands=['decrease_len'])
def decrease_len(message):
  global MAX_LEN
  if MAX_LEN > 25:
    MAX_LEN -= 25
    bot.send_message(message.chat.id, 'Уменьшил максимальное количество букв до {}'.format(MAX_LEN))
  else:
    bot.send_message(message.chat.id, 'Куда меньше то? :(')

@bot.message_handler(commands=['continue'])
def continue_text(message):
  global last_generated
  generated_story = generate_text(last_generated, len(last_generated) + MAX_LEN).split('')[0]
  last_generated = generated_story 

  bot.send_message(message.chat.id, generated_story)

@bot.message_handler(content_types=['text'])
def generate_story(message):
  global last_generated
  generated_story = generate_text(message.text, min(MAX_LEN, len(message.text))).split('<s>')[0]
  last_generated = generated_story

  bot.send_message(message.chat.id, generated_story)

while True:
    bot.polling(none_stop=True)
