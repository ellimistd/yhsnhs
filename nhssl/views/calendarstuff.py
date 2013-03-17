import time
import datetime
import smtplib

def email(Subject, To, Text, AppURL):
    From = "do_not_reply@"+AppURL[7:]
    Body = "From: "+From+"\r\nTo: "+To+"\r\nSubject: "+Subject+"\r\n\r\n"+Text
    print Body
    server = smtplib.SMTP("xenophanes.arlington.k12.va.us")
    server.sendmail(From, [To], Body)
    server.quit()

def class_from_year(year):
    now = datetime.datetime.now()
    if not year:
        return "None"
    if now.year >= int(year):
        return "Senior"
    if now.year == int(year)-1 and now.month > 7:
        return "Senior"
    else:
        return "Junior"


def datetime_from_str(time_str):
    """Return (<scope>, <datetime.datetime() instance>) for the given
    datetime string.
    
    >>> _datetime_from_str("2009")
    ('year', datetime.datetime(2009, 1, 1, 0, 0))
    >>> _datetime_from_str("2009-12")
    ('month', datetime.datetime(2009, 12, 1, 0, 0))
    >>> _datetime_from_str("2009-12-25")
    ('day', datetime.datetime(2009, 12, 25, 0, 0))
    >>> _datetime_from_str("2009-12-25 13")
    ('hour', datetime.datetime(2009, 12, 25, 13, 0))
    >>> _datetime_from_str("2009-12-25 13:05")
    ('minute', datetime.datetime(2009, 12, 25, 13, 5))
    >>> _datetime_from_str("2009-12-25 13:05:14")
    ('second', datetime.datetime(2009, 12, 25, 13, 5, 14))
    >>> _datetime_from_str("2009-12-25 13:05:14.453728")
    ('microsecond', datetime.datetime(2009, 12, 25, 13, 5, 14, 453728))
    """
    formats = [
        # <scope>, <pattern>, <format>
        ("year", "YYYY", "%Y"),
        ("month", "YYYY-MM", "%Y-%m"),
        ("day", "YYYY-MM-DD", "%Y-%m-%d"),
        ("hour", "YYYY-MM-DD HH", "%Y-%m-%d %H"),
        ("minute", "YYYY-MM-DD HH:MM", "%Y-%m-%d %H:%M"),
        ("second", "YYYY-MM-DD HH:MM:SS", "%Y-%m-%d %H:%M:%S"),
        # ".<microsecond>" at end is manually handled below
        ("microsecond", "YYYY-MM-DD HH:MM:SS", "%Y-%m-%d %H:%M:%S"),
    ]
    for scope, pattern, format in formats:
        if scope == "microsecond":
            # Special handling for microsecond part. AFAIK there isn't a
            # strftime code for this.
            if time_str.count('.') != 1:
                continue
            time_str, microseconds_str = time_str.split('.')
            try:
                microsecond = int((microseconds_str + '000000')[:6])
            except ValueError:
                continue
        try:
            t = datetime.datetime.strptime(time_str, format)
        except ValueError:
            pass
        else:
            if scope == "microsecond":
                t = t.replace(microsecond=microsecond)
            return t
    else:
        raise ValueError("could not determine date from %r: does not "
            "match any of the accepted patterns ('%s')"
            % (time_str, "', '".join(s for s,p,f in formats)))
#This was written by Trent Mick and found online.  It's useful, but python really should have it by default
