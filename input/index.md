title: Тоже мне радио
mpos: 1
no_flattr: yes
---
{{ play_file("http://stream.tmradio.net:8180/live.mp3", False) }}

_English?  Read [an introduction](/english.html)._

Добро пожаловать на сайт некоммерческой [открытой][open] сетевой радиостанции
«Тоже мне радио».  Станция вещает круглые сутки [свободную музыку][music],
[новости][news] и [подкасты][pc], иногда прерываясь на [прямые эфиры](/live/) и
[специальные программы](/programs/) (всё доступно [в записи][sub]).  Работает в
автономном режиме, управляется в основном [роботами][robots].  Слушатели влияют
на плейлист [голосуя за песни](/voting/) и напрямую [запрашивая их](/blog/10/).

Работа над станцией координируется в [публичном трекере][gc], частично
описывается в [блоге](/blog/), [финансируется](/support/donate/) слушателями.

<iframe src="http://www.facebook.com/plugins/like.php?href=http%3A%2F%2Fwww.facebook.com%2Ftmradio&amp;layout=button_count&amp;show_faces=false&amp;width=150&amp;action=like&amp;colorscheme=light&amp;height=21" scrolling="no" frameborder="0" style="border:none; overflow:hidden; width:150px; height:21px;" allowTransparency="true"></iframe>
{{ page.get("flattr_button", "") }}


## Последние записи

{{ pagelist(pages, limit=5, label="podcast", show_dates=True) }}

Остальные записи можно найти [в архиве](/podcast/).


[news]: http://echo.msk.ru/news/
[open]: /about/
[pc]: /podcast/
[music]: /music/
[robots]: robots.html
[sub]: rss/
[gc]: /tracker/
