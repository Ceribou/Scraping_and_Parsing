import os 
import logging
import csv
import scrapy
from scrapy.crawler import CrawlerProcess

# Get the top 5 cities and the associated ids
city_ids = {}
with open('cities_list.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        city_ids[row[1]] = row[0]

class Booking_Kayak(scrapy.Spider):

    name = "booking"
    start_urls = ['https://www.booking.com/']

    def parse(self, response):

        for city, city_id in city_ids.items() :
            yield scrapy.FormRequest.from_response(
                response,
                formdata={'ss': city},
                callback=self.hotels_urls,
                meta={'city_id' : city_id}
            )

    def hotels_urls(self, response):
        url = response.css('h3.aab71f8e4e a::attr(href)').getall()
        for link in url :
            yield response.follow(link, callback=self.hotels_details, meta=response.meta)
    
    def hotels_details(self, response):
        yield {
            "name": response.xpath('//h2[@class="d2fee87262 pp-header__title"]/text()').get(),
            "note": response.xpath('//*[@id="js--hp-gallery-scorecard"]/a/div/div/div/div[1]/text()').get(),
            "presentation_text": response.xpath('//*[@id="property_description_content"]/div/p/text()').get(),
            "url": response.url,
            "city_id": response.meta['city_id'],
            "gps_hotel": response.xpath('//a[@id="hotel_sidebar_static_map"]/@data-atlas-latlng').get()
        }
            
# Name of the file where the results will be saved
filename = "booking_spider.json"

# If file already exists, delete it before crawling (because Scrapy will 
# concatenate the last and new results otherwise)
if filename in os.listdir('data/'):
        os.remove('data/' + filename)


process = CrawlerProcess(settings = {
    'USER_AGENT': 'Chrome/124.0',
    'LOG_LEVEL': logging.INFO,
    'AUTOTHROTTLE_ENABLED' : True,
    'DOWNLOADER_MIDDLEWARES' : {
        'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
    },
    "FEEDS": {
       'data/' + filename : {"format": "json"}
    }
})

# Start the crawling using the spider you defined above
process.crawl(Booking_Kayak)
process.start()