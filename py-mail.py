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
import email, base64, re, datetime

EXTENSION_NAME="py-mail"
EXTENSION_VERSION="0.1.0"
EXTENSION_DESCRIPTION="Filter emails by header and body."

cache = {"filename": "", "message": None}

# loads a message from a file or gets it from the cache
def __load_message__(filename):
	msg = None

	if cache["filename"] != filename:
		try:
			with open(filename) as f:
				msg = email.message_from_file(f)

				cache["filename"] = filename
				cache["message"] = msg

		except:
			pass
	else:
		msg = cache["message"]

	return msg

# loads a message and returns the value of the specified header
def __get_header__(filename, key):
	msg = __load_message__(filename)

	if not msg is None:
		return  msg.get(key)

def mail_check_header(filename, key, value):
	v = __get_header__(filename, key)

	if not v is None:
		return value.lower() in v.lower()

	return False

mail_check_header.__signature__=[str, str]

def mail_has_header(filename, key):
	msg = __load_message__(filename)

	if not msg is None:
		return msg.has_key(key)

	return False

mail_has_header.__signature__=[str]

def mail_contains(filename, query):
	def search_payload(msg, query):
		if msg.get_content_type() == "text/plain":
			text = None

			if msg.get("Content-Transfer-Encoding") == "base64":
				text = base64.b64decode(msg.get_payload())
			else:
				text = msg.get_payload()

			if not text is None:
				return query in text

		return False

	msg = __load_message__(filename)

	if not msg is None:
		if msg.get_content_type() == "text/plain":
			return search_payload(msg, query)
		elif msg.is_multipart():
			for part in msg.walk():
				if search_payload(part, query):
					return True

	return False

mail_contains.__signature__=[str]

def mail_find_attachment(filename, query):
	msg = __load_message__(filename)

	if not msg is None and msg.is_multipart():
		l = [p.get_filename().lower() for p in msg.walk() if p.get_filename() is not None]
		return any(filter(lambda a: query.lower() in a, l))

	return False

mail_find_attachment.__signature__=[str]

def mail_has_attachment(filename):
	msg = __load_message__(filename)

	if not msg is None and msg.is_multipart():
		return any([part.get_filename() for part in msg.walk()])

	return False

# converts a date string (yyyy-MM-dd HH:mm:ss) to a N-tuple
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
			else:
				if m.lastindex == 2 and (int(m.group(2)) < 0 or int(m.group(2)) > 12):
					t = None
	return t

# converts a found date header to a 6-tuple
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

# compares a date string (yyyy-MM-dd HH:mm:ss) to the value of the given header
def __compare_dates__(filename, key, datestr, f):
	v = __get_header__(filename, key)

	a = __parse_time_arg__(datestr)
	b = __parse_date_header__(v)

	if not a is None and not b is None:
		if len(a) >= 3:
			b = b[:len(a)] + ([0] * (6 - len(a)))
			a = a + ([0] * (6 - len(a)))

			a, b = map(lambda t: apply(datetime.datetime, t), [a, b])

			return f(a, b)

		elif len(a) == 2:
			return f(a[0], b[0]) or (a[0] == b[0] and f(a[1], b[1]))
		else:
			return f(a[0], b[0])

	return False

def mail_date_equals(filename, key, datestr):
	v = __get_header__(filename, key)
	a = __parse_time_arg__(datestr)
	b = __parse_date_header__(v)

	if not a is None and not b is None:
		return a == b[:len(a)]

	return False

mail_date_equals.__signature__=[str]

def mail_date_before(filename, key, datestr):
	return __compare_dates__(filename, key, datestr, lambda a, b: a > b)

mail_date_before.__signature__=[str, str]

def mail_date_after(filename, key, datestr):
	return __compare_dates__(filename, key, datestr, lambda a, b: a < b)

mail_date_after.__signature__=[str, str]

mail_from = lambda f, q: mail_check_header(f, "From", q)
mail_from.__signature__=[str]

mail_to = lambda f, q: mail_check_header(f, "To", q)
mail_to.__signature__=[str]

mail_subject = lambda f, q: mail_check_header(f, "Subject", q)
mail_subject.__signature__=[str]

mail_sent = lambda f, q: mail_date_equals(f, "Date", q)
mail_sent.__signature__=[str]

mail_sent_before = lambda f, q: mail_date_before(f, "Date", q)
mail_sent_before.__signature__=[str]

mail_sent_after = lambda f, q: mail_date_after(f, "Date", q)
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
