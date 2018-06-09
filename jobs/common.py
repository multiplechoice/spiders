import datetime

import bleach
import re

months = {
    1: u'jan',
    2: u'feb',
    3: u'mars',
    4: [u'apr\u00edl', u'apr'],
    5: u'ma\u00ed',
    6: u'j\u00fan\u00ed',
    7: u'j\u00fal\u00ed',
    8: u'\u00e1g\u00fast',
    9: u'sept',
    10: u'okt',
    11: u'n\u00f3v',
    12: u'des',
}


def decode_date_string(date_string=None):
    """
    Handles parsing abbreviated localised date strings into an ISO8601 compatible timestamp.

    Args:
        date_string (:obj: `unicode`, optional): unicode string with the extracted date

    Examples:
        >>> decode_date_string(None)
        
        >>> decode_date_string(u'27. apr\u00edl 2011')
        '2011-04-27'
    
        >>> decode_date_string(u'1. ma\u00ed.')
        '2018-05-01'
    
    """
    if date_string is None:
        # for when the input is None, re simply return
        return

    if not isinstance(date_string, unicode):
        # only support unicode strings, the theory being that they will properly represent characters
        # and thus match when the regex is used
        return

    regex = re.compile(r'(?P<date>\d+). (?P<month>\w+)([. ]+)?(?P<year>\d+)?', re.UNICODE)
    match = regex.match(date_string)
    date = int(match.group('date'))
    month = translate_month(match.group('month'))
    year = match.group('year')
    # in some instances we don't have a specified year, it's assumed to be obvious in the context of the listing
    # just use the current year as a shortcut for now
    # TODO: make this work for dates that wrap over a year boundary
    if year is None:
        year = datetime.datetime.utcnow().year

    return '{}-{:02}-{:02}'.format(year, month, date)


def translate_month(month):
    """
    Translates the month string into an integer value 
    Args:
        month (unicode): month string parsed from the website listings.

    Returns:
        int: month index starting from 1
    
    Examples:
        >>> translate_month(u'jan')
        1
    """
    for key, values in months.iteritems():
        if month in values:
            return key


def clean_html(input_html):
    allowed_tags = bleach.sanitizer.ALLOWED_TAGS + ['br', 'p']
    cleaner = bleach.sanitizer.Cleaner(tags=allowed_tags, strip=True, strip_comments=True)
    cleaned_lines = []

    if isinstance(input_html, (list, tuple)):
        for line in input_html:
            cleaned_lines.append(cleaner.clean(line).strip())
    elif isinstance(input_html, basestring):
        cleaned_lines.append(cleaner.clean(input_html).strip())

    return '<br>'.join(cleaned_lines)
