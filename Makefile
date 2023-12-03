d ?= $(error Missing required parameter 'd')
t ?= 1
f ?= sample

all:
	poetry run python -m "advent.day_$(d).task_$(t)" data/day_$(d)/$(f).txt
