.PHONY:run
run:
	nohup python3.10 -u BMbot.py >> ./bot.log 2>&1 &

.PHONY:ps
ps:
	ps jax | head -1 && ps jax | grep BMbot.py | grep -v grep