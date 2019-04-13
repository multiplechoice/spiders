from mappings import Base, ScrapedJob
from mappings.utils import create_engine, install_pgcrypto, create_table, create_user, alter_table_owner, session_scope
from jobs.pipelines import PostgresPipeline, ImageDownloader
from jobs.items import JobsItem

from scrapy.exceptions import NotConfigured
from scrapy.utils.test import get_crawler
from scrapy.spiders import Spider
from scrapy.settings import Settings

import pytest
import sqlalchemy  # comes from the sqlalchemy-mappings dependencies
import mock


# use the setup/teardown logic from sqlalchemy-mappings/test_sessions.py
SUPERUSER = 'postgresql://postgres@localhost:5432/jobdb'
DIRK = 'postgresql://dirk_gently@localhost:5432/jobdb'


@pytest.fixture(scope='module')
def db():
    engine = create_engine(SUPERUSER)
    install_pgcrypto(engine)
    try:
        # if a test fails, then we might have a user left over *shrug*
        create_user(engine, 'dirk_gently')
    except sqlalchemy.exc.ProgrammingError:
        pass

    create_table(engine)
    alter_table_owner(engine, 'dirk_gently', 'scraped-jobs')
    yield engine
    # drop the table we created
    Base.metadata.drop_all(engine)
    # and remove the extension
    engine.execute("""DROP EXTENSION IF EXISTS pgcrypto;""")
    # finally, clean up the created user
    engine.execute("""DROP ROLE IF EXISTS dirk_gently;""")


def test_postgres_environment_variable():
    # ensure we get the expected exception when not specifying credentials
    with pytest.raises(NotConfigured):
        PostgresPipeline.from_crawler(get_crawler())

    # empty strings should raise NotConfigured
    with pytest.raises(NotConfigured):
        crawler = get_crawler(settings_dict={'PG_CREDS': ''})
        PostgresPipeline.from_crawler(crawler)

    # as do NoneTypes
    with pytest.raises(NotConfigured):
        crawler = get_crawler(settings_dict={'PG_CREDS': None})
        PostgresPipeline.from_crawler(crawler)

    # and that it works when we do
    crawler = get_crawler(settings_dict={'PG_CREDS': 'frrrrp'})
    assert isinstance(PostgresPipeline.from_crawler(crawler), PostgresPipeline)


def test_postgres_initialisation():
    crawler = get_crawler(settings_dict={'PG_CREDS': DIRK})
    pipeline = PostgresPipeline.from_crawler(crawler)
    assert pipeline.stats.get_value('postgresql/add') is None
    assert pipeline.stats.get_value('postgresql/modify') is None
    assert pipeline.stats.get_value('postgresql/ignore') is None


def test_postgres_statistics():
    crawler = get_crawler(settings_dict={'PG_CREDS': DIRK})
    pipeline = PostgresPipeline.from_crawler(crawler)
    job = JobsItem(spider='test', url='http://fake/job/advert.html', company='Project Blackwing')
    spider = Spider('fake.com')

    # create a mock for the db session so we can control the response
    pipeline.session = mock.MagicMock()
    pipeline.session.query.return_value.filter.return_value.one_or_none.return_value = None
    # if the lookup returns nothing, then the new job is added to the db
    pipeline.process_item(job, spider)

    assert pipeline.stats.get_value('postgresql/add') == 1
    assert pipeline.stats.get_value('postgresql/modify') is None
    assert pipeline.stats.get_value('postgresql/ignore') is None

    # if we try and add the same job again we should get an 'ignore'
    # note that the internal response is the DB representation of the job
    ScrapedJob.from_dict(dict(job))
    pipeline.session.query.return_value.filter.return_value.one_or_none.return_value = ScrapedJob.from_dict(dict(job))
    pipeline.process_item(job, spider)

    assert pipeline.stats.get_value('postgresql/add') == 1
    assert pipeline.stats.get_value('postgresql/modify') is None
    assert pipeline.stats.get_value('postgresql/ignore') == 1

    # now if we modify the job, and readd it we should trigger a 'modify'
    job['title'] = 'Test Subject'
    pipeline.process_item(job, spider)

    assert pipeline.stats.get_value('postgresql/add') == 1
    assert pipeline.stats.get_value('postgresql/modify') == 1
    assert pipeline.stats.get_value('postgresql/ignore') == 1


def test_postgres_insert(db):
    crawler = get_crawler(settings_dict={'PG_CREDS': DIRK})
    pipeline = PostgresPipeline.from_crawler(crawler)
    test_subject = JobsItem(spider='a', url='http://subject.html', company='Project Blackwing', title='Test Subject')
    director = JobsItem(spider='a', url='http://director.html', company='Project Blackwing', title='Director')

    # we don't _need_ to provide the `spider` since it's not used, but is required for the inherited
    # function signature
    spider = Spider('fake.com')
    pipeline.open_spider(spider)
    # as above, the `spider` argument isn't used, but required for the inherited signature
    pipeline.process_item(test_subject, spider)
    pipeline.process_item(director, spider)
    pipeline.close_spider(spider)

    # similar to tests in sqlalchmey-mappings/test_sessions.py
    with session_scope(DIRK) as db_session:
        query = db_session.query(ScrapedJob).filter(ScrapedJob.url == 'http://subject.html')
        result = query.one()
        assert result.url == test_subject['url']
        assert result.data == dict(test_subject)

        query = db_session.query(ScrapedJob).filter(ScrapedJob.url == 'http://director.html')
        result = query.one()
        assert result.url == director['url']
        assert result.spider == director['spider']
        assert result.data == dict(director)


# https://github.com/scrapy/scrapy/blob/1fd1702a11a56ecbe9851ba4f9d3c10797e262dd/tests/test_pipeline_media.py#L18
def _mocked_download_func(request, info):
    response = request.meta.get('response')
    return response() if callable(response) else response


def test_image_downloader_elements():
    # boilerplate taken from  Scrapy code base
    # https://github.com/scrapy/scrapy/blob/1fd1702a11a56ecbe9851ba4f9d3c10797e262dd/tests/test_pipeline_media.py#L28
    spider = Spider('fake.com')
    pipeline = ImageDownloader('s3://frrp/', download_func=_mocked_download_func, settings=Settings(None))
    pipeline.open_spider(spider)

    # we need fake results to allow subsequent parsing of the item; we're not really fussed about this
    # so it's a ittle over-engineered, since we just want to make sure that if a valid item, with downloaded
    # image(s) then we just append the s3 path to the dict
    results = [(True, {
        'checksum': '22f7de7bfadfc4d1b35b2c3346e852e0',
        'path': 'full/1df880943176207c4fb32ad59e0ce68c50285e8a.jpg',
        'url': 'https://www.mbl.is/static/generic/2019/04/11/b4389bbc-0eca-4354-842b-80b2a05be489.jpg'
    })]
    item = {'company': 'Hljómahöll',
            'deadline': '2019-04-28',
            'description': '<p> </p>',
            'image_urls': ['https://www.mbl.is/static/generic/2019/04/11/b4389bbc-0eca-4354-842b-80b2a05be489.jpg'],
            'posted': '2019-04-11',
            'spider': 'mbl',
            'title': 'Tæknistjóri Hljómahallar',
            'url': 'https://www.mbl.is/atvinna/5307/'}
    output = pipeline.item_completed(results, item, pipeline.spiderinfo)
    # the pipeline(s) should have added an 'images' element of uploaded images
    assert 'images' in output
    # we've provided only 1 entry in 'image_urls' so expect only 1 output
    assert len(output['images']) == 1
    # the resulting data should contain the 's3_path' key
    data = output['images'][0]
    assert 's3_path' in data
    # the 's3_path' should end with the path, of the file that's been uploaded
    assert data['s3_path'].endswith(data['path'])
