import openai
import discord
import json

client = discord.Client()

with open('keys.json', 'r') as f:
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

    if message.channel.id in channels and len(message.content) > 8:
        if message.content.startswith("$"):
            response = openai.Completion.create(
                engine="curie",
                prompt=message.content[1:],
                temperature=0.2,
                max_tokens=128,
                top_p=1,
                frequency_penalty=0.5,
                presence_penalty=0,
                stop=["\n\n"]
            )

            responses = response["choices"]
            sorted_responses = sorted(responses, reverse=True, key=lambda x: len(x["text"]))

            await message.channel.send(message.content[1:] + sorted_responses[0]["text"])

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
