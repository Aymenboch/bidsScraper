import scrapy
from scrapy.selector import Selector
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from procurement_project.items import NoticeItem

class UNGMSpider(scrapy.Spider):
    name = 'ungm_spider'
    allowed_domains = ['ungm.org']
    start_urls = ['https://www.ungm.org/Public/Notice']
    LOG_LEVEL = 'DEBUG'    

    def __init__(self):
        super(UNGMSpider, self).__init__()
        options = Options()
        options.add_argument('log-level=1')
        service = Service('C:/Program Files (x86)/chromedriver.exe')
        self.driver = webdriver.Chrome(service=service, options=options)
        self.BASE_URL = "https://www.ungm.org"
    custom_settings = {
        'ITEM_PIPELINES': {
            'procurement_project.pipelines.ExcelExportPipeline': 301,
        }
    }


    def scroll_down(self):
        i = 0
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while i < 4:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            i += 1

    def parse(self, response):
        self.driver.get(response.url)
        # Click on the checkboxes
        checkboxes = ['#RequestForProposal', '#RequestForPreQualification', '#InvitationToBid', '#NotSet', '#RequestForEoi', 
                      '#RequestForQuotation', '#RequestForInformation', '#GrantSupportCallForProposal', '#PreBidNotice', '#IndividualConsultant']
        for checkbox in checkboxes:
            self.driver.find_element(By.CSS_SELECTOR, checkbox).click()

        self.driver.find_element(By.ID, 'lnkShowUNSPSC').click()
        wait = WebDriverWait(self.driver, 10)
        popup = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'ui-dialog')))
        
        # Input and submit filter codes
        filter_codes = "80100000, 80101500, 80101600, 80101601, 80101602, 80101603, 80101604, 80101605, 80101606, 80101607, 80101700, 80101702, 80101703, 80101704, 80101706, 80111500, 80171500, 80171501, 80171502, 80171503, 80171504, 80171505, 80171900, 80171902, 80171903, 80171904, 80171905, 80171906, 80171907, 80171908, 80171909, 80172000, 80172001, 80172002, 80172003, 80172100, 80172101, 80172102, 80172103, 80172104, 81111500, 81111501, 81111502, 81111503, 81111504, 81111505, 81111506, 81111507, 81111508, 81111509, 81111510, 81111511, 81111512, 81111700, 81111701, 81111702, 81111703, 81111704, 81111705, 81111706, 81111707, 81111708, 81111709, 81120000, 81121500, 81121501, 81121502, 81121503, 81121504, 81121505, 84110000, 84111500, 84111600, 84111700, 84111800"
        checked_codes = ["80100000", "81111500", "81111700"]
        input_element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "unspsc-filter-textbox")))
        input_element.send_keys(filter_codes)
        
        inputs = popup.find_elements(By.CLASS_NAME, "unspsc-node-checkbox")
        for input in inputs:
            label_element = input.find_element(By.XPATH, "./following-sibling::label")
            span_text = label_element.find_element(By.CSS_SELECTOR, "span:nth-of-type(1)").text
            print(span_text)
            if span_text in checked_codes:
                input.click()
            
        time.sleep(2)  
        popup.find_element(By.CLASS_NAME, "unspsc-action-submit").click()
        self.driver.find_element(By.ID, "lnkSearch").click()
        time.sleep(2)  
        self.scroll_down()

        # Processing offers
        soup = BeautifulSoup(self.driver.page_source, "lxml")
        offers = soup.select("div.tableRow.dataRow.notice-table")
        for i, offer in enumerate(offers):
            if i >= 50:
                break
        
            div = offer.find("div", attrs={"class":"ungm-flex-row ungm-flex-row--space-between"})
            more_info_link = div.find('a', href=True)['href']
            full_link = self.BASE_URL + more_info_link
            self.driver.get(full_link)
            
            soup_detail = BeautifulSoup(self.driver.page_source, 'lxml')
            item = NoticeItem()
            
            # Extract detailed project information
            project_title = soup_detail.find("span", attrs={"class": "title"}).text.strip() if soup_detail.find("span", attrs={"class": "title"}) else "N/A"
            rows = soup_detail.select(".ungm-col-sm-12 .row")
            descriptions = [row.find_all('span')[1].text.strip() for row in rows if len(row.find_all('span')) > 1]
            
            details = []
            bigparent = soup_detail.find('div', class_='ungm-panel')
            if bigparent:
                bigparent_divs = bigparent.find_all('div', class_='ungm-list-item')
                if len(bigparent_divs) > 1:
                    second_ungm_list_item = bigparent_divs[1]
                    child_divs = second_ungm_list_item.find_all('div')
                    if len(child_divs) > 1:
                        target_div = child_divs[1]
                        paragraphs = target_div.find_all('p')
                        details = [paragraph.text.strip().replace(u'\xa0', u' ') for paragraph in paragraphs]
            
                        item['Project_Title'] = project_title
                        item['Country'] = descriptions[1] if len(descriptions) > 1 else "N/A"
                        item['Registration_Level'] = descriptions[2] if len(descriptions) > 2 else "N/A"
                        item['Publish_Date'] = descriptions[3] if len(descriptions) > 3 else "N/A"
                        item['Deadline'] = descriptions[4] if len(descriptions) > 4 else "N/A"
                        item['Detail'] = details

                        yield item
                        time.sleep(2)

    def closed(self, reason):
        self.driver.quit()
