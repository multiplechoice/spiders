from jobs.items import JobsItem
from jobs.spiders import alfred, mbl, tvinna

from scrapy.http.request import Request
from scrapy.http.response.html import HtmlResponse


def make_response(html):
    response = HtmlResponse('http://fake', encoding='utf8', body=html, request=Request('http://fake'))
    response.meta['item'] = JobsItem()
    return response


def load_file(path):
    with open(path) as handle:
        return make_response(handle.read())


def test_mbl_parse():
    # make a spider and get the root page
    spider = mbl.MblSpider()
    root = load_file('tests/data/mbl/mbl.html')
    # ensure the length is right
    assert len(list(spider.parse(root))) == 3
    from_parse_method = [
        JobsItem(spider='mbl', url='http://fake/mbl-contains-image.html'),
        JobsItem(spider='mbl', url='http://fake/mbl-company-name-with-link.html'),
        JobsItem(spider='mbl', url='http://fake/mbl-company-name-plain.html')
    ]
    # the mbl.parse method only extracts certain elements, such as the spide name and parsed url
    for job in spider.parse(root):
        # ensure that the parsed item is in the expected result set
        assert job.meta['item'] in from_parse_method


def test_mbl_parse_specific_job():
    spider = mbl.MblSpider()
    assert list(spider.parse_specific_job(load_file('tests/data/mbl/job-contains-image.html'))) == [JobsItem(
        company='Reykjahlíðarskóli',
        deadline='2019-04-23',
        description='<p> </p><p><strong>Lausar eru til umsóknar kennarastöður\xa0við Reykjahlíðarskóla í '
            'Mývatnssveit\xa0frá 1. ágúst 2019.</strong></p>\n<p>Um er að ræða umsjónarkennslu á unglingastigi,'
            ' stærðfræði, náttúrufræði, íþróttir, textílmennt og heimilisfræði.</p>',
        file_urls=[
            'http://fake/f7a81019-b164-4360-a8e3-7b87f42dcbb0.jpg'
        ],
        posted='2019-04-09',
        title='Grunnskólakennarar'
    )]
    assert list(spider.parse_specific_job(load_file('tests/data/mbl/job-company-name-with-link.html'))) == [JobsItem(
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
        title='Safnstjóri'
    )]
    assert list(spider.parse_specific_job(load_file('tests/data/mbl/job-company-name-plain.html'))) == [JobsItem(
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
        title='Hjúkrunarfræðingur'
    )]


def test_tvinna_parse_node():
    # setup spider and load feed
    spider = tvinna.TvinnaSpider()
    root = load_file('tests/data/tvinna/feed.xml')
    # make sure the length is correct
    assert len(list(spider.parse(root))) == 1
    # check the parsed elements
    for job in spider.parse(root):
        assert job.meta['item'] == JobsItem(
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


def test_tvinna_parse_specific_job():
    spider = tvinna.TvinnaSpider()
    assert list(spider.parse_specific_job(load_file('tests/data/tvinna/job.html'))) == [JobsItem(
        company='TACTICA'
    )]


def test_alred_parse():
    # load spider and API response
    spider = alfred.AlfredSpider()
    feed = load_file('tests/data/alfred/feed.json')
    # ensure we got the expected number of job listings
    assert len(list(spider.parse(feed))) == 1
    for job in spider.parse(feed):
        # check the parsed response
        assert job.meta['item'] == JobsItem(
            company='Landspítali',
            spider='alfred',
            url='https://alfred.is/starf/26565'
        )


def test_alfred_parse_specific_job():
    # setup spider
    spider = alfred.AlfredSpider()
    assert list(spider.parse_specific_job(load_file('tests/data/alfred/job.json'))) == [JobsItem(
        deadline='2019-04-29T00:00:00',
        description='<p><strong>L&aelig;knaritari</strong></p>\n<p>Starf l&aelig;knaritara &aacute; Mi&eth;st&ouml;'
            '&eth; um sj&uacute;kraskr&aacute;rritun er laust til ums&oacute;knar. Deildin er sta&eth;sett &iacute; '
            'K&oacute;pavogi og fer &thorn;ar fram ritun sj&uacute;kraskr&aacute;r fyrir s&eacute;rgreinar &aacute; '
            'Landsp&iacute;tala. &THORN;ar starfar fj&ouml;lmennur h&oacute;pur l&aelig;knaritara og skrifstofumanna '
            'vi&eth; fj&ouml;lbreytt verkefni. Starfi&eth; er unni&eth; &iacute; vaktavinnu.<br> <br> &Aacute;hersla '
            'er &aacute; teymisvinnu og g&oacute;&eth;a &thorn;j&oacute;nustu vi&eth; kl&iacute;n&iacute;ska '
            'starfsmenn me&eth; g&aelig;&eth;i, &ouml;ryggi og stefnu LSH a&eth; lei&eth;arlj&oacute;si.</p>\n<p>'
            '<strong>Helstu verkefni og &aacute;byrg&eth;</strong></p>\n<ul>\n<li>Ritun sj&uacute;kraskr&aacute;a '
            'fyrir Landsp&iacute;tala</li>\n<li>Fagleg &aacute;byrg&eth; &aacute; skrifum og g&ouml;gnum sem fylgja '
            'sj&uacute;krask&yacute;rslum</li>\n</ul>\n<p><strong>H&aelig;fnikr&ouml;fur</strong></p>\n<ul>\n<li>'
            'Frumkv&aelig;&eth;i og metna&eth;ur &iacute; starfi</li>\n<li>&Ouml;gu&eth;, sj&aacute;lfst&aelig;&eth; '
            'og skipul&ouml;g&eth; vinnubr&ouml;g&eth;</li>\n<li>J&aacute;kv&aelig;tt vi&eth;m&oacute;t</li>\n<li>Gott'
            ' vald &aacute; &iacute;slensku og ensku</li>\n<li>L&ouml;ggilding &iacute; l&aelig;knaritun</li>\n</ul>\n'
            '<p><strong>Frekari uppl&yacute;singar um starfi&eth;</strong></p>\n<p>Laun samkv&aelig;mt gildandi '
            'kjarasamningi sem fj&aacute;rm&aacute;la- og efnahagsr&aacute;&eth;herra og SFR - st&eacute;ttarf&eacute;'
            'lag &iacute; almanna&thorn;j&oacute;nustu hafa gert. Teki&eth; er mi&eth; af jafnr&eacute;ttisstefnu LSH '
            'vi&eth; r&aacute;&eth;ningar &iacute; st&ouml;rf &aacute; Landsp&iacute;tala.</p>\n<p>Starfi&eth; er '
            'laust n&uacute; &thorn;egar e&eth;a eftir samkomulagi. Ums&oacute;kn fylgi n&aacute;ms- og starfsferilskr'
            '&aacute; &aacute;samt afriti af pr&oacute;fsk&iacute;rteinum og starfsleyfi. &Ouml;llum ums&oacute;knum '
            'ver&eth;ur svara&eth;.<br> <br> Landsp&iacute;tali er lifandi og fj&ouml;lbreyttur vinnusta&eth;ur '
            '&thorn;ar sem um 6000 manns starfa &iacute; &thorn;verfaglegum teymum og samstarfi &oacute;l&iacute;kra '
            'fagst&eacute;tta. Framt&iacute;&eth;ars&yacute;n Landsp&iacute;tala er a&eth; vera h&aacute;sk&oacute;la'
            'sj&uacute;krah&uacute;s &iacute; fremstu r&ouml;&eth; &thorn;ar sem sj&uacute;klingurinn er &aacute;vallt'
            ' &iacute; &ouml;ndvegi. Lykil&aacute;herslur &iacute; stefnu sp&iacute;talans eru &ouml;ryggismenning, '
            'skilvirk og v&ouml;ndu&eth; &thorn;j&oacute;nusta, uppbygging mannau&eth;s og st&ouml;&eth;ugar '
            'umb&aelig;tur.</p>\n<p>Starfshlutfall er 50 - 100%<br> Ums&oacute;knarfrestur er til og me&eth; '
            '29.04.2019</p>\n<p><strong>N&aacute;nari uppl&yacute;singar veitir</strong><br>Selma Gu&eth;nad&oacute;'
            'ttir - selma@landspitali.is - 543 7260</p>\n<p><br> Landsp&iacute;tali<br> Mi&eth;st&ouml;&eth; um '
            'sj&uacute;kraskr&aacute;rritun<br> K&oacute;pavogsger&eth;i 2<br> 200 K&oacute;pavogur</p>\n<p><br> '
            '&nbsp;</p>',
        posted='2019-04-11T10:47:00',
        title='Læknaritari - Miðstöð sjúkraskrárritunar'
    )]