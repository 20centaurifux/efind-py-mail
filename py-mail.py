"""
    project............: efind-py-mail
    description........: efind extension to filter emails.
    date...............: 07/2017
    copyright..........: Sebastian Fedrau

    Permission is hereby granted, free of charge, to any person obtaining
    a copy of this software and associated documentation files (the
    "Software"), to deal in the Software without restriction, including
    without limitation the rights to use, copy, modify, merge, publish,
    distribute, sublicense, and/or sell copies of the Software, and to
    permit persons to whom the Software is furnished to do so, subject to
    the following conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
    IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
    OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
    OTHER DEALINGS IN THE SOFTWARE.
"""
import os, email, base64, re, datetime, mailbox

EXTENSION_NAME="py-mail"
EXTENSION_VERSION="0.1.0"
EXTENSION_DESCRIPTION="Filter emails by header and body."

cache = {"filename": "", "content": None}

# Tests if the sequence seq contains an element where pred(x) returns logical True.
def some(pred, seq):
    if not seq is None:
        for e in seq:
            if pred(e):
                return True

    return False

# Tests if text contains haystack. The string comparison is case insensitive.
def in_str(text, haystack):
    if not text is None and not haystack is None:
        return haystack.lower() in text.lower()

    return False

# Loads messages from a file.
def __load_file__(filename):
    result = None

    def make_mbox_generator(values):
        for msg in values:
            yield email.message_from_string(msg.as_string())

    if cache["filename"] != filename:
        try:
            # get file extension:
            _, ext = os.path.splitext(filename)

            # try to load mbox file:
            if ext == "" or ext.lower() == ".mbox":
                mbox = mailbox.mbox(filename)
                values = mbox.values()

                if len(values) > 0:
                    result = make_mbox_generator(values)
                    cache["format"] = "mbox"
                    cache["messages"] = values

            # no mbox file loaded => try to create single message from file:
            if result is None:
                with open(filename) as f:
                    result = [email.message_from_file(f)]
                    cache["format"] = "message"
                    cache["messages"] = result

            cache["filename"] = filename

        except:
            pass
    else:
        if cache["format"] == "mbox":
            result = make_mbox_generator(cache["messages"])
        else:
            result = cache["messages"]

    return result

def mail_check_header(filename, key, value):
    return some(lambda m: in_str(m.get(key), value), __load_file__(filename))

mail_check_header.__signature__=[str, str]

def mail_has_header(filename, key):
    return some(lambda m: m.has_key(key), __load_file__(filename))

mail_has_header.__signature__=[str]

def mail_contains(filename, query):
    def search_payload(msg, query):
        if msg.get_content_type() == "text/plain":
            text = None

            try:
                if msg.get("Content-Transfer-Encoding") == "base64":
                    text = base64.b64decode(msg.get_payload())
                else:
                    text = msg.get_payload()
            except:
                pass

            if not text is None:
                return query in text

        return False

    def search_message(msg, query):
        if not msg is None:
            if msg.get_content_type() == "text/plain":
                return search_payload(msg, query)
            elif msg.is_multipart():
                return some(lambda p: search_payload(p, query), msg.walk())

    return some(lambda m: search_message(m, query), __load_file__(filename))

mail_contains.__signature__=[str]

def mail_find_attachment(filename, query):
    content = __load_file__(filename)

    f = lambda p: p.get_filename() is not None and in_str(p.get_filename(), query)

    return some(lambda m: m.is_multipart() and some(f, m.walk()), content)

mail_find_attachment.__signature__=[str]

def mail_has_attachment(filename):
    content = __load_file__(filename)

    f = lambda p: p.get_filename() is not None

    return some(lambda m: m.is_multipart() and some(f, m.walk()), content)

# Converts a date string (yyyy-MM-dd HH:mm:ss) to a N-tuple.
def __parse_time_arg__(arg):
    t = None

    groups = [r"(\d{4})", r"-(\d{1,2})", r"-(\d{1,2})", r" (\d{1,2})", r":(\d{1,2})", r":(\d{1,2})"]
    pattern = ""

    for g in groups:
        pattern += g
        m = re.match("^%s$" % pattern, arg)

        if not m is None:
            t = map(int, m.groups())

            if m.lastindex >= 3:
                try:
                    apply(datetime.datetime, t + [0] * (6 - len(t)))
                except:
                    t = None
            elif m.lastindex == 2 and (int(m.group(2)) < 0 or int(m.group(2)) > 12):
                t = None

    return t

# Converts a found date header to a 6-tuple.
def __parse_date_header__(value):
    t = None

    if not value is None:
        t = email.utils.parsedate_tz(value)

        if not t is None:
            dt = datetime.datetime.fromtimestamp(email.utils.mktime_tz(t))
            t = [dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second]
        else:
            t = email.utils.parsedate(v)

            if not t is None:
                t = list(b[:6])

    return t

# Compares a date string (yyyy-MM-dd HH:mm:ss) to the value of the given header.
def __compare_dates__(msg, key, datestr, pred):
    v = msg.get(key)
    a = __parse_time_arg__(datestr)
    b = __parse_date_header__(v)

    if not a is None and not b is None:
        if len(a) >= 3:
            b = b[:len(a)] + ([0] * (6 - len(a)))
            a = a + ([0] * (6 - len(a)))

            a, b = map(lambda t: apply(datetime.datetime, t), [a, b])

            return pred(a, b)
        elif len(a) == 2:
            return pred(a[0], b[0]) or (a[0] == b[0] and pred(a[1], b[1]))
        else:
            return pred(a[0], b[0])

    return False

def mail_date_equals(filename, key, datestr):
    def date_equals(msg, key, datestr):
        v = msg.get(key)
        a = __parse_time_arg__(datestr)
        b = __parse_date_header__(v)

        if not a is None and not b is None:
            return a == b[:len(a)]

        return False

    return some(lambda m: date_equals(m, key, datestr), __load_file__(filename))

mail_date_equals.__signature__=[str, str]

def mail_date_before(filename, key, datestr):
    return some(lambda m: __compare_dates__(m, key, datestr, lambda a, b: a > b), __load_file__(filename))

mail_date_before.__signature__=[str, str]

def mail_date_after(filename, key, datestr):
    return some(lambda m: __compare_dates__(m, key, datestr, lambda a, b: a < b), __load_file__(filename))

mail_date_after.__signature__=[str, str]

def mail_from(filename, value):
    return mail_check_header(filename, "From", value)

mail_from.__signature__=[str]

def mail_to(filename, value):
    return mail_check_header(filename, "To", value)

mail_to.__signature__=[str]

def mail_subject(filename, value):
    return mail_check_header(filename, "Subject", value)

mail_subject.__signature__=[str]

def mail_sent(filename, value):
    return mail_date_equals(filename, "Date", value)

mail_sent.__signature__=[str]

def mail_sent_before(filename, value):
    return mail_date_before(filename, "Date", value)

mail_sent_before.__signature__=[str]

def mail_sent_after(filename, value):
    return mail_date_after(filename, "Date", value)

mail_sent_after.__signature__=[str]

EXTENSION_EXPORT=[mail_check_header,
                  mail_has_header,
                  mail_contains,
                  mail_find_attachment,
                  mail_has_attachment,
                  mail_date_equals,
                  mail_date_before,
                  mail_date_after,
                  mail_from,
                  mail_to,
                  mail_subject,
                  mail_sent,
                  mail_sent_before,
                  mail_sent_after]
