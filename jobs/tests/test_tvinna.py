from jobs.spiders.tvinna import get_page_id


def test_page_id():
    assert get_page_id(u'Tvinna \u2013 Skapandi st\xf6rf \xe1 \xcdslandi') == 1
    assert get_page_id(u'Tvinna \u2013 Page 2') == 2
