from mappings import Base
from mappings.utils import create_engine, install_pgcrypto, create_table, create_user, alter_table_owner
from jobs.pipelines import PostgresPipeline
from jobs.items import JobsItem

from scrapy.exceptions import NotConfigured
from scrapy.utils.test import get_crawler
import pytest
import sqlalchemy  # comes from the sqlalchemy-mappings dependencies


# use the setup/teardown logic from mappings/test_sessions.py
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


def test_environment_variable():
    # ensure we get the expected exception when not specifying credentials
    with pytest.raises(NotConfigured):
        PostgresPipeline.from_crawler(get_crawler())

    # and that it works when we do
    crawler = get_crawler(settings_dict={'PG_CREDS': 'frrrrp'})
    assert isinstance(PostgresPipeline.from_crawler(crawler), PostgresPipeline)


def test_initialisation(db):
    crawler = get_crawler(settings_dict={'PG_CREDS': DIRK})
    pipeline = PostgresPipeline.from_crawler(crawler)
    assert pipeline.stats.get_value('postgresql/add') is None
    assert pipeline.stats.get_value('postgresql/modify') is None
    assert pipeline.stats.get_value('postgresql/ignore') is None


def test_adding_items(db):
    crawler = get_crawler(settings_dict={'PG_CREDS': DIRK})
    pipeline = PostgresPipeline.from_crawler(crawler)
    job = JobsItem(spider='test', url='http://fake/job/advert.html', company='Project Blackwing')
    # we don't need to provide the `spider` since it's not used, but is required for the inherited
    # function signature
    spider = None
    pipeline.open_spider(spider)
    # as above, the `spider` argument isn't used, but required for the inherited signature
    pipeline.process_item(job, spider)

    assert pipeline.stats.get_value('postgresql/add') == 1
    assert pipeline.stats.get_value('postgresql/modify') is None
    assert pipeline.stats.get_value('postgresql/ignore') is None

    # if we try and add the same job again we should get an 'ignore'
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

    pipeline.close_spider(spider)
