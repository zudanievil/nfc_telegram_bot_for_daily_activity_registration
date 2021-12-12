# инструкция по установке
## linux
```bash
# 1. клонировать репозиторий
git clone https://...
cd ...

# шаги 2-5 могут быть заменены скриптом:
sudo bash env_setup.sh
# --------
# 2. поставить python
sudo apt install python3-virtualenv   # debian, ubuntu
sudo dnf install python3-virtualenv    # fedora, centos

# 3. создать виртуальную среду python
virtualenv -p python3 env
# 4. активировать среду
source env/bin/activate
# 5. установить библиотеки
pip install -r requirements.txt
# ---------

# 6. запустить src/telebot.py
python3 src/telebot.py [telegram_bot_token] [bot_email] [bot_email_password] [log_mode]
# log mode: debug | info | critical
 ```
токен, почта, пароль от почты и тд в файле `bot_info.yml`.
тк он содержит информацию для аутентификации в боте и в почте

## windows
1. крайне желательно установить chocolatey (менеджер пакетов): https://chocolatey.org/install#install-step2
```
# 2. установить git, клонировать репозиторий
git clone https://...
cd ...

# 3 - 6 аналогичны шагам 2-5 для linux:
call env_setup.bat

# 7. запустить src/telebot.py

```