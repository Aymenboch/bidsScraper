import scrapy
from scrapy.spiders import Spider
import json
from procurement_project.items import ProcurementItem  

class ProcurementSpider(Spider):
    name = 'worldbank'
    allowed_domains = ['worldbank.org']
    
    def __init__(self, number, *args, **kwargs):
        super(ProcurementSpider, self).__init__(*args, **kwargs)
        self.number = number  # Save the passed number
        self.start_urls = [
            f'https://search.worldbank.org/api/v2/procnotices?format=json&fct=procurement_group_desc_exact,notice_type_exact,procurement_method_code_exact,procurement_method_name_exact,project_ctry_code_exact,project_ctry_name_exact,regionname_exact,rregioncode,project_id,sector_exact,sectorcode_exact&fl=id,bid_description,project_ctry_name,project_name,notice_type,notice_status,notice_lang_name,submission_date,noticedate&srt=submission_date%20desc,id%20asc&apilang=en&rows={self.number}&srce=both&os=0'
        ]
    custom_settings = {
        'FEED_EXPORT_FIELDS': ['project_name', 'notice_type', 'region', 'notice_date', 'bid_description', 'sector_description'],
        'ITEM_PIPELINES': {
            'procurement_project.pipelines.ProcurementProjectPipeline': 300,
        }
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7,es;q=0.6,ar;q=0.5",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    }
    
    
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse_api, headers=self.headers, meta={'page_count': 1})

    def parse_api(self, response):
        data = json.loads(response.text)
        for offer in data.get('procnotices', []):
            offer_id = offer['id']
            offer_url = f"https://search.worldbank.org/api/v2/procnotices?format=json&apilang=en&fl=*&id={offer_id}"
            yield scrapy.Request(offer_url, callback=self.parse_offer, headers=self.headers)

        # Pagination logic
        page_count = response.meta['page_count']
        if page_count < self.number:
            next_offset = int(response.url.split("os=")[-1]) + 20
            next_page_url = response.url.split("os=")[0] + "os=" + str(next_offset)
            yield scrapy.Request(next_page_url, callback=self.parse_api, headers=self.headers, meta={'page_count': page_count + 1})

    def parse_offer(self, response):
        data = json.loads(response.text)
        if 'procnotices' in data and len(data['procnotices']) > 0:
            item_data = data['procnotices'][0]  # Get the first item in the 'procnotices' list
        else:
            return  # Exit if no data is found
        
        item = ProcurementItem()
        item['project_name'] = item_data.get('project_name', 'none')
        item['notice_type'] = item_data.get('notice_type', 'none')
        item['region'] = item_data.get('regionname', 'none')
        item['notice_date'] = item_data.get('noticedate', 'none')
        item['bid_description'] = item_data.get('bid_description', 'none')
        
        sectors = item_data.get('sector', [])
        item['sector_description'] = [sector.get('sector_description', 'none') for sector in sectors]
        
        yield item

