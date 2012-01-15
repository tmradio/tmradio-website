all: build

rebuild: fetch update-dl-counts build update-money commit

build:
	mkdir -p output
	rm -rf output/*
	cat scripts/*.js > input/scripts.js
	python poole.py --build > build.log

commit:
	-git add -A -q
	-git commit -q input -am "Source update"
	-git push -q

update-money:
	python tools/update-money.py > /tmp/yandex-money.csv
	mv /tmp/yandex-money.csv input/support/donate/yandex/history.csv

fetch:
	-git pull -q

serve:
	poole.py --serve

update-dl-counts:
	python poolemonkey/feeds.py tmradio/tsn tmradio/all tmradio/prokino tmradio/mcast tmradio/podcast tmradio/live sosonews umonkey/podcast umonkey > input/dlstats.csv

update-schedule:
	python tools/update-schedule.py

clean:
	find . -name '*.pyc' -delete

process-hotline: fetch
	python poole.py --build
	-git add -q input/hotline
	-git commit -q input/hotline -m "New hotline pages."
	git push -q

twit-hotline:
	for fn in input/hotline/????????/??????; do \
		touch $$fn/twit_sent; \
		echo $$fn; \
	done

fix-duration:
	python tools/fix-duration.py
