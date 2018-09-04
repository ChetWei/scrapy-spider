# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    #需要爬取的url
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):

        #获取下一页的url，并交给scrapy进行下载
        #1.获取文章列表页的文章url并交给解析函数进行具体字段分析
        # 2.获取下一页的url交给scrapy进行下载，下载完成交给scrapy

        #解析列表页的所有文章url并交给scrapy下载后进行解析
        post_nodes = response.css("#archive .")
        for post_node in post_nodes:
            image_url = post_node.xpath(r'/img/@src').extract_first("")
            post_url = post_node.xpath(r'/@href').extract_first("")
            yield Request(url=parse.urljoin(response.url,post_url),meta={'front_image_url':image_url},callback=self.parse_detail)

        #提取下一页并交给scrapy进行下载
        next_url = response.xpath(r'//*[@id="archive"]//a[contains(@class,"next")]/@href').extract()[0]
        if next_url:
            yield Request(url=parse.urljoin(response.url,next_url),callback=self.parse)·





    """提取文章的具体内容"""
    def parse_detail(self,response):
        front_image_url = response.meta.get("front_image_url","")

        title =  response.xpath(r'//div[@class="entry-header"]/h1/text()').extract()[0].strip()
        crate_date = response.xpath(r'//div[@class="entry-meta"]/p[1]/text()[1]').extract()[0].strip().replace('·','').strip()

        #点赞数
        praise_nums = response.xpath(r"//span[contains(@class,'vote-post-up')]/h10[1]/text()").extract()
        if  praise_nums :
            praise_nums = int(praise_nums[0].strip())
        else:
            praise_nums = 0

        #收藏数
        fav_nums = response.xpath(r'//span[contains(@class,"bookmark-btn")]/text()').extract()[0]
        match_re = re.match(r'.*(\d+)',fav_nums)
        if match_re:
            fav_nums = int(match_re.group().strip())
        else:
            fav_nums = 0

        #评论数
        commont_nums = response.xpath(r'//a[@href="#article-comment"]/text()').extract()
        if commont_nums :
            commont_nums = commont_nums[0].strip()  #'1 评论'
            match_re = re.match(r'(\d+)', commont_nums)
            commont_nums = int(match_re.group())
        else:
            commont_nums = 0




        #文章内容
        content = response.xpath(r'//div[@class="entry"]').extract()[0]

        tag_list = response.xpath(r'//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        tag_list = [element for element in tag_list if not element.strip().endswith('评论')]
        tags = ','.join(tag_list)

        pass


