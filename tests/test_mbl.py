from jobs.spiders.mbl import get_company_name

from scrapy.http.response.html import HtmlResponse


def make_response(html):
    return HtmlResponse("http://fake", encoding="utf8", body=html)


def test_company_names():
    # this one has a link formatted title from https://www.mbl.is/atvinna/5295/
    assert (
        get_company_name(
            make_response(
                """<div class="section title-wrapper">
            <p class="ad_created">Sett inn: 9. apr.</p>
                <a href="https://km.is/frettir/" target="_blank" class="company-link" rel="noopener noreferrer">KM þjónustan ehf.</a>
            <h1 class="title"> Starf á bifreiðaverkstæði í Búðardal</h1>
        </div>"""
            )
        )
        == "KM þjónustan ehf."
    )
    # this one has a plain text company name from https://www.mbl.is/atvinna/5296/
    assert (
        get_company_name(
            make_response(
                """<div class="section title-wrapper">
            <p class="ad_created">Sett inn: 9. apr.</p>
                <h4 class="sub-title">Reykjahlíðarskóli</h4>
            <h1 class="title"> Grunnskólakennarar</h1>
        </div>"""
            )
        )
        == "Reykjahlíðarskóli"
    )
