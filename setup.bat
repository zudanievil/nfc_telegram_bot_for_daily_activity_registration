choco install python3
python3 -m pip install --user virtualenv
python3 -m -venv env
call env/scripts/activate
pip install -r requirements.txt

mkdir storage
touch storage/chip.txt
