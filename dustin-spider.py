import scrapy


class QuotesSpider(scrapy.Spider):
    name = "dustin"
    start_urls = [
        'https://www.dustinhome.fi/group/laitteistot/tietokoneet-tabletit/kannettavat-tietokoneet/gaming/',
    ]

    def parse(self, response):
        for quote in response.css('div.p_listTmpl1'):
            yield {
                'name': quote.css('div.p_name a::text').get().strip(),
                'description': quote.css('div.p_desc::text').get(),
				'price': quote.css('div.p_price::text').get().strip().strip('\u20ac').replace(',','.').replace('\xa0',''),
				'link': 'https://www.jimms.fi/'+quote.css('div.p_name a::attr(href)').get(),
            }

        next_page = response.xpath('//li[not(@class="disabled")]/a[@data-bind="click: moveToNextPage"]/@href').get()
        if next_page is not None:
           yield response.follow(next_page, callback=self.parse)