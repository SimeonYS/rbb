import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import RbbItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class RbbSpider(scrapy.Spider):
	name = 'rbb'
	start_urls = ['https://ir.rbbusa.com/news-releases?items_per_page=10&page=0']

	def parse(self, response):
		post_links = response.xpath('//div[@class="views-field-field-nir-news-title"]/a[@hreflang="en"]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//li[@class="pager__item pager__item--next"]/a/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)


	def parse_post(self, response):
		date = response.xpath('(//div[@class="field__item"])[2]/text()').get().split(' at')[0]
		title = response.xpath('//div[@class="field__item"]/text()').get()
		content = response.xpath('//div[@class="node__content"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=RbbItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
