import scrapy

class ProcurementItem(scrapy.Item):
    project_name = scrapy.Field()
    notice_type = scrapy.Field()
    region = scrapy.Field()
    notice_date = scrapy.Field()
    bid_description = scrapy.Field()
    sector_description = scrapy.Field()
    
class NoticeItem(scrapy.Item):
    Project_Title = scrapy.Field()
    Country = scrapy.Field()
    Registration_Level = scrapy.Field()
    Publish_Date = scrapy.Field()
    Deadline = scrapy.Field()
    Detail = scrapy.Field()
