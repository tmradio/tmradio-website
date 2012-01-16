all: build

rebuild: fetch update-dl-counts build update-money commit

build:
	mkdir -p output
	rm -rf output/*
	cat scripts/*.js > input/scripts.js
	python poole.py --build > build.log

commit:
	-git add -A
	-git commit -q input -m "Source update"
	-git push -q

update-money:
	python tools/update-money.py > /tmp/yandex-money.csv
	mv /tmp/yandex-money.csv input/support/donate/yandex/history.csv
	-git commit -q input/support/donate/yandex/history.csv -m "Обновление истории Яндекс.Денег (автомат)"
	-git push -q

fetch:
	-git pull -q

serve:
	python poole.py --serve

update-dl-counts:
	python poolemonkey/feeds.py tmradio/tsn tmradio/all tmradio/prokino tmradio/mcast tmradio/podcast tmradio/live sosonews umonkey/podcast umonkey > input/dlstats.csv

update-schedule:
	python tools/update-schedule.py
	-git commit -q input/schedule.txt input/schedule.ical -m "Обновление расписания эфиров (автомат)"
	-git push -q

clean:
	find . -name '*.pyc' -delete

process-hotline: fetch
	python poole.py --build
	-git add input/hotline
	-git commit -q input/hotline -m "New hotline pages."
	git push -q

twit-hotline:
	for fn in input/hotline/????????/??????; do \
		touch $$fn/twit_sent; \
		echo $$fn; \
	done

fix-duration:
	python tools/fix-duration.py
