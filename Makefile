sample1:
	poetry run python -m "advent.day_$(d).task_1" data/day_$(d)/sample.txt

input1:
	poetry run python -m "advent.day_$(d).task_1" data/day_$(d)/input.txt

sample2:
	poetry run python -m "advent.day_$(d).task_2" data/day_$(d)/sample.txt

input2:
	poetry run python -m "advent.day_$(d).task_2" data/day_$(d)/input.txt