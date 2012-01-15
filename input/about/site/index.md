title: Об этом сайте
---
Сайт статический, HTML-код генерируется из разметки Markdown с помощью
[Poole][1].  Исходный код лежит на [GitHub][2].  Статистика посещений
[общедоступна][3] (Яндекс.Метрика).


## Инструкция по редактированию сайта

Для работы с кодом сайта нужно [зарегистрироваться][5] в Гитхабе, затем
клонировать репозиторий:

    git clone git@github.com:tmradio/tmradio-website.git

Исходные файлы появятся в папке `tmradio-website/src/input`.  После их
редактирования нужно, находясь в папке `tmradio-website/src`, выполнить команду
`make update`; эта команда получит из репозитория обновления (на случай, если
кто-то их внёс за время редактирования (см. [роботы][4])), обновит HTML код
страниц и отправит всё это в репозиторий.

Poole входит в комплект (есть в репозитории), однако для работы ему нужна
библиотека json.  Установить её в системе Debian или Ubuntu можно так:

    sudo apt-get install python-json

[1]: https://bitbucket.org/obensonne/poole/src
[2]: https://github.com/tmradio/tmradio-website
[3]: http://metrika.yandex.ru/stat/?id=10892923
[4]: /robots.html
[5]: https://github.com/signup/free
