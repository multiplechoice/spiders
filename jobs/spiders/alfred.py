import json
import urllib.parse

import dateutil.parser
import scrapy

from jobs.common import clean_html
from jobs.items import JobsItem


class AlfredSpider(scrapy.Spider):
    name = "alfred"
    start_urls = ["https://api.alfred.is/api/v3/web/open/jobs?cat=0&limit=100&page=0"]

    def parse(self, response):
        # we're using an api rather than scraping a website so we need to grok the json response
        content = json.loads(response.text)
        # each job under the 'data' key refers to companies listed in the `included` key, so to make
        # it easy to get at the data we make a dict keyed to the id of the company
        included_data = {entry["id"]: entry for entry in content["included"]}

        for job in content["data"]:
            job_id = job["id"]
            company_id = job["relationships"]["brand"]["data"]["id"]

            item = JobsItem()
            item["spider"] = self.name
            item["company"] = included_data[company_id]["attributes"]["name"]
            item["url"] = urllib.parse.urljoin("https://alfred.is/starf/", job_id)

            api_url = urllib.parse.urljoin(
                "https://api.alfred.is/api/v3/web/open/jobs/", job_id
            )
            request = scrapy.Request(api_url, callback=self.parse_specific_job)
            request.meta["item"] = item
            yield request

    def parse_specific_job(self, response):
        content = json.loads(response.text)
        job = content["data"]["attributes"]
        # included = content['included']

        item = response.meta["item"]
        item["title"] = job["title"]
        item["posted"] = dateutil.parser.parse(job["start"]).isoformat()
        item["description"] = clean_html(job["body"])
        if "deadline" in job:
            item["deadline"] = dateutil.parser.parse(job["deadline"]).isoformat()

        # item['tags'] = []
        # for each in included:
        #     if each['type'] in ('jobtag', 'category'):
        #         item['tags'].append(each['attributes']['name'])

        yield item
