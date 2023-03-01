import openai
import discord
import json
import os

intents = discord.Intents.all()
client = discord.Client(intents=intents)

with open('GPT3_discord_bot/keys.json', 'r') as f:
  data = json.load(f)

bot_key =  data['bot-key']
openai.api_key = data['GPT3-api-key']

channels = [930578203557396551,
           930583898356863008]

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.id in channels and len(message.content) > 5:
        if message.content.startswith("$"):

            completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo", 
                    messages=[{"role": "user", "content": "Tell the world about the ChatGPT API in the style of a pirate."}]
                )

            #print(completion)
            #responses = response["choices"]
            #sorted_responses = sorted(responses, reverse=True, key=lambda x: len(x["text"]))

            await message.channel.send(completion)

        if message.content.startswith("?"):
            response = openai.Completion.create(
                engine="curie",
                prompt=message.content[1:] + " The answer is",
                temperature=0.2,
                max_tokens=128,
                top_p=1,
                frequency_penalty=0.5,
                presence_penalty=0,
                stop=["\n\n"]
            )

            responses = response["choices"]
            sorted_responses = sorted(responses, reverse=True, key=lambda x: len(x["text"]))



            await message.channel.send("I think" + sorted_responses[0]["text"])


client.run(bot_key)
