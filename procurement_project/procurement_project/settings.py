ITEM_PIPELINES = {
   'procurement_project.pipelines.ProcurementProjectPipeline': 300,
   'procurement_project.pipelines.ExcelExportPipeline': 301,
}

BOT_NAME = 'procurement_project'
LOG_LEVEL = 'DEBUG'
SPIDER_MODULES = ['procurement_project.spiders']
DEFAULT_REQUEST_HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}
NEWSPIDER_MODULE = 'procurement_project.spiders'