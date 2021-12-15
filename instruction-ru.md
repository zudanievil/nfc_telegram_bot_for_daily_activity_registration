# инструкция по установке
## linux
```bash
# 1. клонировать репозиторий
git clone https://github.com/zudanievil/nfc_telegram_bot_for_daily_activity_registration
cd nfc_telegram_bot_for_daily_activity_registration

# 2 запустить установочный скрипт
sudo bash setup.sh

# 3. запустить src/telebot.py
python3 src/telebot.py [process_name] [telegram_bot_token] [bot_email] [bot_email_password] [log_mode]
# log mode: debug | info | critical

# желательно открепить процесс от терминала, например:
nohup python3 src/telebot.py [process_name] [telegram_bot_token] [bot_email] [bot_email_password] [log_mode] > storage/out.log 2>&1 &
# (https://danielbeard.wordpress.com/2011/06/08/detaching-a-running-process-from-a-bash-shell/)

# 4. остановить бота
kill -s TERM -l "$(pidof [process_name])"
 ```
токен, почта, пароль от почты и тд в файле `bot_info.yml`.
тк он содержит информацию для аутентификации в боте и в почте

## windows [пока не проверен!]
1. крайне желательно установить chocolatey (менеджер пакетов): https://chocolatey.org/install#install-step2
```
# 2. установить git, клонировать репозиторий
git clone https://github.com/zudanievil/nfc_telegram_bot_for_daily_activity_registration
cd nfc_telegram_bot_for_daily_activity_registration

# 3.
call env_setup.bat

# 4. запустить src/telebot.py

```