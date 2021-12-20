# инструкция по установке
## linux
```bash
# 1. клонировать репозиторий
git clone https://github.com/zudanievil/nfc_telegram_bot_for_daily_activity_registration
cd nfc_telegram_bot_for_daily_activity_registration

# 2. запустить установочный скрипт
sudo bash setup.sh

# 2,5. скопировать файл конфигурации в папку ./private (если есть)

# 3. запустить src/telebot.py
python3 src/telebot.py
# log mode: debug | info | critical

# 4. остановить бота
kill -s TERM -l "$(pidof [process_name])"

# при запуске "в продакшене" лучше открепить процесс от терминала:
bash launch.sh  # предполагается, что в конфигруации стоит опция "log_to_console": false

# остановить:
bash terminate.sh
# (https://danielbeard.wordpress.com/2011/06/08/detaching-a-running-process-from-a-bash-shell/)
 ```
 пароли и тд, относящиеся к боту хранить в папке `private/` их нельзя выкладывать в открытый доступ.

## windows [пока не проверен!]
1. крайне желательно установить chocolatey (менеджер пакетов): https://chocolatey.org/install#install-step2
```
# 2. установить git, клонировать репозиторий
git clone https://github.com/zudanievil/nfc_telegram_bot_for_daily_activity_registration
cd nfc_telegram_bot_for_daily_activity_registration

# 3.
call setup.bat

# 4. запустить src/telebot.py

```
