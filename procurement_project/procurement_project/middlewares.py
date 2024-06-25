from scrapy import signals

class ProcurementProjectSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # Scrapy manages the process without it.

    def process_request(self, request, spider):
        # Called for each request that goes through the spider middleware.
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request() raises an exception.
        pass

class ProcurementProjectDownloaderMiddleware:
    # Same structure as Spider Middleware
    pass
