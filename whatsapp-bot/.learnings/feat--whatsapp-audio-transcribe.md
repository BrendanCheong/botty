# Learnings
Writing down my learnings from this feature as I develop the audio-transcription feature for this WhatsApp Bot

## WhatsApp Bot
- Surprisingly a lot more difficult to configure than Telegram bots. WhatApp has a lot of layers of security baked into it where you have to prove that you are a real person/business before even creating a bot.
- I had to register myself as a WhatsApp Business before proceeding with using Twilio to setup a WhatsApp bot, and even then Twilio had to confirm my identity to make sure I'm a real person so I wouldn't use
the phone number attached to the bot to spam people
- So majority of the time spent building the bot was centered around configuring Twilio.

## Robyn
- Decided to use Robyn framework because it was fast and could support multiple threads
- Personally find the Robyn framework very interesting due to its Speed since its implemented in Rust
- But as of 1st Feb 2026, the lack of Pydantic support and no v1.0 release makes Robyn a bit of a dealbreaker when it comes to production

## Kew
- Decided to use Kew, a new python queue library from my friend Rach
- Found it to be quite good, especially since arq was already deprecated for quite some time.
- Would be interested to explore this library more in the future to see how it goes.

## Translations
- I found the OpenAI whisper model not so good for detecting Chinese and English mixed into the audio
- So I'm sticking to GPT-4o despite it being costlier
- At first I thought of transcribing --> then translating, but I think GPT-4o is good enough to handle both instead of calling the LLM twice.
