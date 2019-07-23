import scrapy
import re

class QuotesSpider(scrapy.Spider):
    name = "gigantti"
    base_url = 'https://www.gigantti.fi/INTERSHOP/web/WFS/store-gigantti-Site/fi_FI/-/EUR/ViewStandardCatalog-AjaxPaging?CategoryDomainName=store-gigantti-ProductCatalog&CategoryName=fi-pelikannettavat&SortingAttribute=ProductListPrice-asc&SearchParameter=&@QueryTerm=*&ContextCategoryUUID=fDCsGQV5jjMAAAFavHQMCISy&discontinued=0&online=1&PageNumber=%d'
    page = 0
    start_urls = [ base_url % page]
    previous_id='TESTITESTIJOO'

    def parse(self, response):
        top_id = response.xpath('//div[@class="product-number sku rsNoDrag"]/text()').get()
        if self.previous_id != top_id and self.page < 20:
            for href in response.css('a.product-name::attr(href)'):
                yield response.follow(href, self.parse_name)
                
            self.page = self.page + 1
            print(top_id)
            print(self.previous_id)
            self.previous_id = top_id
            yield scrapy.Request(self.base_url % self.page)
    
    def parse_name(self, response):
        item = {}
        item['name'] = response.css('h1.product-title::text').get()
        item['link'] = response.request.url
        item['price'] = response.css('div.product-price-container span::text').get().replace('\xa0','')
        item['outlet'] = response.xpath('//div[@class="product-price align-left any-1-1 margin-1"]/div[@class="price-promotion any-1-1 price-promotion-table margin-1"]/following::text()').get().strip('\n')
        
        details_url = 'https://www.gigantti.fi/INTERSHOP/web/WFS/store-gigantti-Site/fi_FI/-/EUR//CC_AjaxProductTab-Get?ProductSKU=%s&TemplateName=CC_ProductSpecificationTab&PageletUUID=undefined'
        product_id = response.xpath('//p[@class="sku discrete"]/@data-product-sku').get()
        request = scrapy.Request(details_url % product_id, self.parse_laptop_details)
        request.meta['item'] = item
        yield request
    
    def parse_laptop_details(self, response):
        item = response.meta['item']
        gpu = response.xpath('//td[@data-md-value-id="30877"]/text()').get()
        pattern = re.compile("nvidia ", re.IGNORECASE)
        pattern2 = re.compile("amd ", re.IGNORECASE)
        if 'nvidia' in gpu.lower():
            gpu = pattern.sub("", gpu)
        if 'geforce' not in gpu.lower() and ('gtx' in gpu.lower() or 'rtx' in gpu.lower()):
            gpu = 'GeForce ' + gpu
        if 'amd' in gpu.lower():
            gpu = pattern2.sub("", gpu)
        
        screen = response.xpath('//td[@data-md-value-id="31376"]/text()').get()
        screen_type = response.xpath('//td[@data-md-value-id="31550"]/text()').get()
        if screen_type:
            screen = screen +' '+ screen_type
        
        storage = response.xpath('//td[@data-md-value-id="31400"]/text()').get()
        storage_total = response.xpath('//td[@data-md-value-id="31508"]/text()').get()
        if storage_total:
            storage = storage + ' '+storage_total + 'GB'

        item['gpu'] = gpu
        item['cpu'] = response.xpath('//td[@data-md-value-id="31586"]/text()').get()
        item['os'] = response.xpath('//td[@data-md-value-id="31027"]/text()').get()
        item['ram'] = response.xpath('//td[@data-md-value-id="31186"]/text()').get()
        item['screen'] = screen
        item['storage'] = storage
        
        yield item