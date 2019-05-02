import scrapy

from jobs.common import decode_date_string, clean_html
from jobs.items import JobsItem


def get_company_name(response):
    # it's possible to give a link with the text, which changes the CSS classes
    return (
        response.css(".sub-title::text").get()
        or response.css(".company-link::text").get()
    )


class MblSpider(scrapy.Spider):
    name = "mbl"
    start_urls = ["http://www.mbl.is/atvinna/"]

    def parse(self, response):
        for job in response.css("ul.list-group"):
            item = JobsItem()
            item["spider"] = self.name

            url = response.urljoin(job.css("a::attr(href)").extract_first())
            item["url"] = url

            request = scrapy.Request(url, callback=self.parse_specific_job)
            request.meta["item"] = item
            yield request

    def parse_specific_job(self, response):
        item = response.meta["item"]
        item["company"] = get_company_name(response)
        item["title"] = response.css("h1.title::text").get().strip()

        item["posted"] = decode_date_string(
            response.css(".ad_created::text").re(r"Sett inn: (.+)")[0]
        )
        item["deadline"] = decode_date_string(
            response.css(".group-wrapper.mt-15 span::text").get()
        )
        item["description"] = clean_html(response.css(".maintext-wrapper").extract())

        # some mbl items are just a title and an image, so we need to save the image and upload it to s3
        # so that we can show it later without hot-linking issues
        image_src = response.css(".img-responsive::attr(src)").extract_first()
        if image_src is not None:
            # adding to the `image_urls` causes this to be picked up by the ImageDownloader plugin
            item["image_urls"] = [response.urljoin(image_src)]

        yield item
