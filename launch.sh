#!/usr/bin/env bash

source "env/bin/activate"
nohup python src/telebot.py > /dev/null 2>&1 &
echo "launched the bot"
