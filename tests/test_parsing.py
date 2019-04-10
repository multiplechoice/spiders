from jobs.items import JobsItem
from jobs.spiders import alfred, mbl, tvinna

from scrapy.http.request import Request
from scrapy.http.response.html import HtmlResponse


def make_response(html):
    response = HtmlResponse('http://fake', encoding='utf8', body=html, request=Request('http://fake'))
    return response


def load_file(path):
    with open(path) as handle:
        return make_response(handle.read())


def test_mbl():
    # create a spider
    spider = mbl.MblSpider()
    # load the root page
    root_page = load_file('tests/data/mbl/mbl.html')
    # create response objects for each of the subpages. these dicts contain both the body HtmlResponse
    # object, and the expected parsed output. they are keyed on the "fake" url that we get from the
    # response object being combined with the page url ie: http://fake + /mbl-contains-image.html
    page_contents = {
        'http://fake/mbl-contains-image.html': load_file('tests/data/mbl/mbl-contains-image.html'),
        'http://fake/mbl-company-name-with-link.html': load_file('tests/data/mbl/mbl-company-name-with-link.html'),
        'http://fake/mbl-company-name-plain.html': load_file('tests/data/mbl/mbl-company-name-plain.html')
    }
    expected_items = {
        'http://fake/mbl-contains-image.html':
            JobsItem(
                company='Reykjahlíðarskóli',
                deadline='2019-04-23',
                description='<p> </p><p><strong>Lausar eru til umsóknar kennarastöður\xa0við Reykjahlíðarskóla í '
                    'Mývatnssveit\xa0frá 1. ágúst 2019.</strong></p>\n<p>Um er að ræða umsjónarkennslu á unglingastigi,'
                    ' stærðfræði, náttúrufræði, íþróttir, textílmennt og heimilisfræði.</p>',
                file_urls=[
                    'http://fake/f7a81019-b164-4360-a8e3-7b87f42dcbb0.jpg'
                ],
                posted='2019-04-09',
                spider='mbl',
                title='Grunnskólakennarar',
                url='http://fake/mbl-contains-image.html'
            ),
        'http://fake/mbl-company-name-with-link.html':
            JobsItem(
                company='Sagnheimar, byggðasafn',
                deadline='2019-04-10',
                description='<p> </p><p>Þekkingarsetur Vestmannaeyja- ÞSV leitar eftir öflugum og hugmyndaríkum '
                    'starfmanni í stöðu safnstjóra Sagnheima, byggðarsafns. Umsækjendur skulu hafa lokið háskólaprófi '
                    'sem nýtist í starfi og búa yfir góðri tölvu- og tungumálakunnáttu. Helstu verkefni safnstjóra eru '
                    'að annast rekstur Sagnheima byggðasafns, vinna að uppsetningu sýninga og varðveislu safngripa. '
                    'Mikilvægt er að umsækjendur búi yfir reynslu eða þekkingu á sviði reksturs og safnamála, hafi til '
                    'að bera frumkvæði, jákvæðni, lipurð í mannlegum samskiptum og hæfileika til að miðla þekkingu. '
                    'Nánari upplýsingar um starfið veitir Páll Marvin Jónsson, framkvæmdastjóri í síma 694-1006. '
                    'Umsóknum ásamt menntunar- og starfsferilskrá skal skila á tölvutæku formi á netfangið pmj@setur.is'
                    ', merkt: Starf safnstjóra.</p>',
                posted='2019-04-03',
                spider='mbl',
                title='Safnstjóri',
                url='http://fake/mbl-company-name-with-link.html'
            ),
        'http://fake/mbl-company-name-plain.html':
            JobsItem(
                company='Hjúkrunarheimilið Hjallatún',
                deadline='2019-05-31',
                description='<p> </p><p></p>\n<p>\xa0</p>\n<p>\xa0</p>\n<p>Staða hjúkrunarfræðings</p>\n<p>'
                    'Hjúkrunarfræðingur óskast til starfa við Hjúkrunarheimilið Hjallatún í Vík. Um er að ræða 80 % '
                    'stöðu verkefnisstjóra 2, \xa0sem vinnur dagvaktir, kvöldvaktir og bakvaktir eftir samkomulagi. '
                    'Staðan er laus frá 1. júlí næstkomandi.</p>\n<p>\xa0</p>\n<p>Leitað er að einstaklingi með áhuga '
                    'á öldrunarmálum, með góða færni í mannlegum samskiptum sem getur unnið sjálfstætt og skipulega.'
                    '\xa0 Laun eru samkvæmt kjarasamningi Sambands íslenskra sveitarfélaga og Félags íslenskra '
                    'hjúkrunarfræðinga. Gott húsnæði á staðnum.</p>\n<p>\xa0</p>\n<p>Allar nánari upplýsingar veitir: '
                    'Guðrún Berglind Jóhannesdóttir hjúkrunarforstjóri, <a href="mailto:hjallatun@vik.is">'
                    'hjallatun@vik.is</a> eða í síma 487-1348.\xa0</p>\n<p>\xa0</p>',
                posted='2019-04-02',
                spider='mbl',
                title='Hjúkrunarfræðingur',
                url='http://fake/mbl-company-name-plain.html'
            )
    }
    for job_listing in spider.parse(root_page):
        specific_page = page_contents[job_listing.url]
        # bind the meta object
        specific_page.meta['item'] = job_listing.meta['item']
        # execute the callback with the specific page for the listing
        for item in job_listing.callback(specific_page):
            # ensure the items match
            assert item == expected_items[job_listing.url]


def test_tvinna():
    # create the spider
    spider = tvinna.TvinnaSpider()
    # load the data
    feed = load_file('tests/data/tvinna/feed.xml')
    # get the listings
    for job_listing in spider.parse(feed):
        # load the specific listing page content
        specific_page = load_file('tests/data/tvinna/tvinna.html')
        # bind the item that's already been parsed from the feed.xml
        specific_page.meta['item'] = job_listing.meta['item']
        # check that the data is as expected
        for item in job_listing.callback(specific_page):
            assert item == JobsItem(
                company='TACTICA',
                description='<p>Vegna aukinna verkefna leitum við nú að sérfræðingi í veflausnum og rekstri vefhýsinga'
                    '.</p>\n\n<p>Helstu verkefni eru að þjónusta viðskiptavini og samstarfsaðila ásamt því að taka '
                    'þátt í almennum rekstri hýsingarumhverfis TACTICA sem rekið er undir nafninu Hýsingar.is og er '
                    'einn af stærri aðilum á hýsingarmarkaðnum í dag.</p>\n\n<p>TACTICA sinnir ekki vefsíðugerð en '
                    'vinnur náið með vefstofum ýmist í þjónustu, ráðgjöf eða almennri aðstoð.</p>\n\n<p>Mikil áhersla '
                    'er lögð á hæfni viðkomandi til þess að vinna með samstarfsaðilum og viðskiptavinum og tryggja að '
                    'öllum verkefnum sé skilað á farsælan og faglegan hátt.</p>\n\n<p>Viðkomandi þarf að hafa góðan '
                    'heildarskilning á þeim kerfum sem unnið er í og því nauðsynlegt að hafa bakgrunn í upplýsingatækni'
                    ' og grunnskilning á vefforritun ásamt mjög góðum skilningi á WordPress.</p>\n\n<p>Framkoma og '
                    'samskiptahæfni eru lykilatriði í þessu starfi.</p>\n\n<p><strong>Helstu verkefni og ábyrgð:'
                    '</strong></p>\n\n<ul>\n<li>Samskipti og ráðgjöf við viðskiptavini og samstarfsaðila</li>\n<li>'
                    'Greining vandamála sem geta komið upp á vefsvæðum notenda</li>\n<li>Aðstoð og vinna með '
                    'samstarfsaðilum TACTICA</li>\n<li>Samskipti við þjónustuaðila og birgja</li>\n<li>Uppsetning og '
                    'umsýsla á sýndarþjónum viðskiptavina</li>\n</ul>\n\n<p><strong>Menntunar- og hæfniskröfur</strong>'
                    '</p>\n\n<ul>\n<li>Menntun eða reynsla sem nýtist starfi.</li>\n<li>Reynsla af hugbúnaðar / '
                    'vefstörfum er mikill kostur.</li>\n<li>Mjög góð tölvukunnátta og skilningur á upplýsingatækni '
                    'skilyrði</li>\n<li>Kerfi sem æskilegt er að viðkomandi hafi reynslu af: WHM/Cpanel, DNS, WordPress'
                    ', Linux og Windows server</li>\n<li>Mjög gott vald á íslensku og ensku, færni til að tjá sig í '
                    'ræðu og riti</li>\n<li>Góð skipulagshæfni, frumkvæði og sjálfstæði í vinnubrögðum er nauðsynleg'
                    '</li>\n</ul>\n\n<p>TACTICA er vaxandi fyrirtæki sem var stofnað árið 2012 og sérhæfir sig í '
                    'heildarlausnum upplýsingatæknimála fyrir minni og meðalstór fyrirtæki ásamt því að reka eitt '
                    'stærsta hýsingarfyrirtæki landsins Hýsingar.is</p>\n\n<p>Einnig erum við leiðandi á sviði '
                    'vöruumsýslu og samþættingarlausna.</p>',
                posted='2019-04-09T19:07:52+00:00',
                spider='tvinna',
                title='Sérfræðingur í veflausnum',
                url='https://www.tvinna.is/jobs/serfraedingur-i-veflausnum/'
            )
