# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import psycopg2

class LaptopcrawlPipeline(object):
    count = 0
    error_count = 0
    def open_spider(self, spider):
        try:
            self.connection = psycopg2.connect(user="postgres",
                                          password="jonttu",
                                          host="localhost",
                                          port="5432",
                                          database="postgres")
        except (Exception, psycopg2.Error) as error :
            if(self.connection):
                print("Failed to insert record into mobile table", error)
            else:
                print("Failed to connect")

    def close_spider(self, spider):
        #closing database connection.
        if(self.connection):
            self.cursor.close()
            self.connection.close()
            print (self.count, "records inserted successfully into table")
            print (self.error_count, "errors encountered during inserts")
            print("PostgreSQL connection is closed")

    def process_item(self, item, spider):
        outlet_price = ''
        if 'gpu' in item:
            graphics = item['gpu']
        if 'cpu' in item:
            cpu = item['cpu']
        if 'os' in item:
            os = item['os']
        if 'ram' in item:
            ram = item['ram']
        if 'screen' in item:
            screen = item['screen']
        if 'storage' in item:
            storage = item['storage']
        if 'outlet' in item:
            outlet_price = item['outlet']
            
        if 'description' in item:
            descrip=item['description'].strip().split(', ')
            for x in descrip:
                if 'geforce' in x.lower() or 'radeon' in x.lower():
#TODO parsi pois gftx ja NVIDIA (tai muuta geforce-> nvidia geforce)
                    graphics = x
                elif x.lower().startswith('intel') or x.lower().startswith('amd'):
                    cpu = x
                elif "SSD" in x or "HDD" in x or "SSHD" in x:
                    storage = x
                elif "DDR" in x or "GB" in x:
                    ram = x
                elif 'win' in x.lower():
                    os = x
                else:
                    screen = x
        try:
            self.cursor = self.connection.cursor()
            postgres_insert_query = """ INSERT INTO laptops ("CPU", "GPU", "LINK", "NAME","OS", "PRICE", "RAM", "SCREEN", "STORAGE", "OUTLET_PRICE") VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            record_to_insert = (cpu,graphics,item['link'],item['name'],os,item['price'],ram,screen, storage, outlet_price)
            self.cursor.execute(postgres_insert_query, record_to_insert)
            self.connection.commit()
            self.count = self.count+1
        except (Exception, psycopg2.Error) as error :
            if(self.connection):
                self.error_count = self.error_count +1
                print("\nERROR: Failed to insert record into mobile table", error)

        return item