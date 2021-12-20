#!/usr/bin/env bash

nohup python src/telebot.py > /dev/null 2>&1 &
echo "launched the bot"
