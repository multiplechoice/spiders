from jobs.spiders.visir import decode_date_string


def test_date_reformating():
    assert decode_date_string(u'05.04.2017') == '2017-04-05'
    assert decode_date_string(u'10.04.2017') == '2017-04-10'
    assert decode_date_string(u'17.04.2017') == '2017-04-17'
    assert decode_date_string(u'23.12.2015') == '2015-12-23'
