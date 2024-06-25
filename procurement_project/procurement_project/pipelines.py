import pandas as pd

class ProcurementProjectPipeline:
    def process_item(self, item, spider):
        # Example: Convert all texts to lowercase
        for field in item.fields:
            item[field] = str(item[field]).lower()
        return item

class ExcelExportPipeline:
    def open_spider(self, spider):
        self.items = []

    def close_spider(self, spider):
        df = pd.DataFrame(self.items)
        print(f"Saving {len(self.items)} items to Excel.")  # Debug statement
        df.to_excel('C:/Users/aayme/Desktop/kpmg/procurement_project/ungm.xlsx', index=False, engine='openpyxl')

    def process_item(self, item, spider):
        self.items.append(dict(item))
        print(f"Processed item: {item}")  # Debug statement
        return item
