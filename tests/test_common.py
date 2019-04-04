from jobs.common import decode_date_string, translate_month
from freezegun import freeze_time


def test_month_lookups():
    assert translate_month(u'jan') == 1
    assert translate_month(u'feb') == 2
    assert translate_month(u'mars') == 3
    assert translate_month(u'apr\u00edl') == 4
    assert translate_month(u'ma\u00ed') == 5
    assert translate_month(u'j\u00fan\u00ed') == 6
    assert translate_month(u'j\u00fal\u00ed') == 7
    assert translate_month(u'\u00e1g\u00fast') == 8
    assert translate_month(u'sept') == 9
    assert translate_month(u'okt') == 10
    assert translate_month(u'n\u00f3v') == 11
    assert translate_month(u'des') == 12


def test_unknown_month():
    assert translate_month('January') is None


def test_decoding_whole_string_from_tvinna():
    assert decode_date_string(u'27. apr\u00edl 2011') == '2011-04-27'
    assert decode_date_string(u'30. \u00e1g\u00fast 2013') == '2013-08-30'
    assert decode_date_string(u'9. ma\u00ed 2014') == '2014-05-09'
    assert decode_date_string(u'10. j\u00fal\u00ed 2014') == '2014-07-10'
    assert decode_date_string(u'3. n\u00f3v. 2014') == '2014-11-03'
    assert decode_date_string(u'3. feb. 2015') == '2015-02-03'
    assert decode_date_string(u'29. feb. 2016') == '2016-02-29'


@freeze_time('1st April, 2017')
def test_decoding_whole_string_from_mbl():
    assert decode_date_string('1. ma\u00ed.') == '2017-05-01'
    assert decode_date_string('10. ma\u00ed.') == '2017-05-10'
    assert decode_date_string('16. apr.') == '2017-04-16'


def test_nonetype():
    # sometimes dates are expected but are empty, meaning we pass a None to the decode function
    assert decode_date_string(None) is None


def test_string_rather_than_unicode_input():
    # if a string is passed in that is not unicode, it won't be handled correctly by
    # the regex so instead we just return, indicating that something isn't right
    assert decode_date_string('27. apr\u00edl 2011') is None
