# efind-py-mail

## Introduction

This extension for [efind](https://github.com/20centaurifux/efind) provides
functions to filter emails. It can read message from eml and mailbox files.

## Date strings

Date strings have to be in the format "yyyy-MM-dd HH:mm:ss". The accuracy depends
on the number of specified fields. Any field (expect the year) is optional.

## Available functions

### mail\_check\_header(string: key, string: value)

Tests if the header *key* of at least one found message contains the string
*value*. The string comparison is case insensitive.

	$ efind . 'mail_check_header("X-Original-To", "john.doe@example.org")'

### mail\_has\_header(string: key)

Tests if the header *key* is set in at least one found message.

	$ efind . 'mail_has_header("X-Virus-Scanned")'

### mail\_contains(string: text)

Tests if the body of at least one found message contains *text*.

	$ efind . 'mail_contains("foobar")'

### mail\_find\_attachment(string: name)

Tests if a filename containing *name* is attached to a at least one found message.
The string comparison is case insensitive.

	$ efind . 'mail_find_attachment("invoice.pdf")'

### mail\_has\_attachment()

Tests if at least one file is attached to a found message.

	$ efind . 'mail_has_attachment()'

### mail\_date\_equals(string: key, string: date)

Converts the header *key* to date and compares it to *date*.

	$ efind . 'mail_date_equals("Date", "2017-07-11 18:11:40")'

### mail\_date\_before(string: key, string: date)

Tests if the date found in the header *key* is greater than *date*.

	$ efind . 'mail_date_before("Date", "2017-07")'

### mail\_date\_after(string: key, string: date)

Tests if *date* is greater than the date found in the header *key*.

	$ efind . 'mail_date_after("Date", "2017-07-01 11:39")'

### mail\_from(string: sender)

Tests if the sender of a found message contains *sender*. The string comparison is
case insensitive.

	$ efind . 'mail_from("Alice") or mail_from("Bob")'

### mail\_to(string: receiver)

Tests if the receiver of a found message contains *receiver*. The string comparison is
case insensitive.

	$ efind . 'mail_from("Bob") and mail_to("Alice")'

### mail\_subject(string: subject)

Tests if the subject of a found message contains *subject*. The string comparison is
case insensitive.

	$ efind . 'mail_from("@acme.org") and mail_subject("invoice")'

### mail\_sent(string: date)

Tests if at least one found message has been sent on *date*.

	$ efind . 'mail_sent("2017")

### mail\_sent\_before(string: date)

Tests if at least one found message has been sent before *date*.

	$ efind . 'mail_sent("2017-01-01")

### mail\_sent\_after(string: date)

Tests if at least one found message has been sent after *date*.

	$ efind . 'mail_sent("2017-01-01 10:36")

## Installation

Copy the Python script to *~/.efind/extensions* or run the *install.sh* shell script.
