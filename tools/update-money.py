# encoding=utf-8

import os
import sys

from yandexmoney import export_history_csv


REPLACE = (
    (u"МТС (Россия): +7 911 774-36-16", u"Оплата хостинга"),
    (u"МТС (Хекс)", u"Оплата хостинга"),
    (u"Магазин PeterHost.Ru", u"Оплата хостинга"),
    (u"Магазин Platron.ru", u"Оплата SMS"),
    (u"Platron.ru", u"Оплата SMS"),

    (u"Пожертвование tmradio.net", u""),
    (u"Перевод от пользователя Яндекс.Денег", u""),
    (u"Перевод с Яндекс.Кошелька", u""),
)


key_file = os.path.expanduser("~/.config/yandexmoney-tmradio.key")
if not os.path.exists(key_file):
    print >> sys.stderr, "Key file not found, not updating transactions."
    exit(1)

output = export_history_csv(key_file)
for k, v in REPLACE:
    output = output.replace(k, v)
print output.encode("utf-8")
