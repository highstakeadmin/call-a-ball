black:
	black .

run:
	python main.py

init:
	conda create -y -n call-a-ball python=3.12
	conda run -n call-a-ball pip install -r requirements.txt

update-requirements:
	conda run -n call-a-ball pip freeze > requirements.txt
