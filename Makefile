all: build

rebuild: fetch update-dl-counts build update-money commit

build:
	mkdir -p output
	rm -rf output/*
	cat javascript/*.js > input/scripts.js
	python scripts/poole.py --build | tee build.log

build-quiet:
	rm -rf output/*
	test -d output || mkdir -p output
	cat javascript/*.js > input/scripts.js
	python scripts/poole.py --build > build.log

debug:
	python scripts/poole.py --build

commit:
	-git add -A
	-git commit -q input -m "Source update"
	-git push -q

push:
	-git push -q

update-money:
	python tools/update-money.py > /tmp/yandex-money.csv
	mv /tmp/yandex-money.csv input/support/donate/yandex/history.csv
	-git commit -m "Обновление истории Яндекс.Денег (автомат)" input/support/donate/yandex/history.csv >/dev/null

fetch:
	-git pull -q

serve:
	python scripts/poole.py --serve

update-dl-counts:
	python poolemonkey/feeds.py tmradio/tsn tmradio/all tmradio/prokino tmradio/mcast tmradio/podcast tmradio/live sosonews umonkey/podcast umonkey > input/dlstats.csv

update-schedule:
	python tools/update-schedule.py
	-git commit -m "Обновление расписания эфиров (автомат)" input/schedule.txt input/schedule.ical >/dev/null

clean:
	find . -name '*.pyc' -delete

process-hotline: fetch
	python scripts/poole.py --build
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
