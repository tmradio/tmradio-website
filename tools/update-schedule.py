# encoding=utf-8

def convert_schedule(src, dst):
    """Converts a text file (src) to the iCalendar format (dst).  Source file
    is expected to contain lines of this format:

    YYYY-MM-DD HH:MM Program
    YYYY-MM-DD HH:MM Program

    Time is expected to be in local timezone, but the output file is written in UTC.

    To validate the output, use http://severinghaus.org/projects/icv/
    """
    import time

    output = u"BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//hacksw/handcal//NONSGML v1.0//EN\r\n"

    for line in file(src, "rb").read().decode("utf-8").split("\n"):
        if not line.strip():
            continue

        ts = time.mktime(time.strptime(line[:16], "%Y-%m-%d %H:%M"))

        ts_beg = time.strftime("%Y%m%dT%H%M%S", time.gmtime(ts))
        ts_end = time.strftime("%Y%m%dT%H%M%S", time.gmtime(ts + 60*60))

        output += u"BEGIN:VEVENT\r\nDTSTART:%(ts_beg)s\r\nDTEND:%(ts_end)s\r\nSUMMARY:%(text)s\r\nEND:VEVENT\r\n" % {
            "ts_beg": ts_beg,
            "ts_end": ts_end,
            "text": line[17:].strip(),
        }

    output += u"END:VCALENDAR"
    file(dst, "wb").write(output.encode("utf-8"))


convert_schedule("input/schedule.txt", "input/schedule.ical")
