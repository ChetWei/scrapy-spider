# -*- coding: utf-8 -*-
import scrapy
import re
from datetime import datetime
from scrapy.http import Request
from scrapy.loader import ItemLoader
from urllib import parse

from ArticleSpider.items import JobBoleArticleItem,ArticleItemLoader
from ArticleSpider.utils import common



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
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        for post_node in post_nodes:
            image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url,post_url),meta={'front_image_url':image_url},callback=self.parse_detail)

        #提取下一页并交给scrapy进行下载
        next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url,next_url),callback=self.parse)





    """提取文章的具体内容"""
    def parse_detail(self,response):

        article_item = JobBoleArticleItem()

        # title =  response.xpath(r'//div[@class="entry-header"]/h1/text()').extract()[0].strip()
        # create_date = response.xpath(r'//div[@class="entry-meta"]/p[1]/text()[1]').extract()[0].strip().replace('·','').strip()
        #
        # #点赞数
        # praise_nums = response.xpath(r"//span[contains(@class,'vote-post-up')]/h10[1]/text()").extract()
        # if  praise_nums :
        #     praise_nums = int(praise_nums[0].strip())
        # else:
        #     praise_nums = 0
        #
        # #收藏数
        # fav_nums = response.xpath(r'//span[contains(@class,"bookmark-btn")]/text()').extract()[0]
        # match_re = re.match(r'.*(\d+)',fav_nums)
        # if match_re:
        #     fav_nums = int(match_re.group().strip())
        # else:
        #     fav_nums = 0
        #
        # #评论数
        # commont_nums = response.xpath(r'//a[@href="#article-comment"]/text()').extract()
        # if commont_nums :
        #     commont_nums = commont_nums[0].strip()  #'1 评论'
        #     match_re = re.match(r'(\d+)', commont_nums)
        #     commont_nums = int(match_re.group())
        # else:
        #     commont_nums = 0
        #
        # #文章内容
        # content = response.xpath(r'//div[@class="entry"]').extract()[0]
        #
        # tag_list = response.xpath(r'//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        # tag_list = [element for element in tag_list if not element.strip().endswith('评论')]
        # tags = ','.join(tag_list)
        #
        #
        # article_item["title"] = title
        # #字符串转换日期
        # try:
        #     create_date = datetime.strptime(create_date,"%Y/%m/%d").date()
        # except Exception as e :
        #     create_date = datetime.now().date()
        #
        # article_item["create_date"] = create_date
        # article_item["url"] =  response.url
        # article_item["url_object_id"] = common.get_md5(response.url)   #md5
        # article_item["front_image_url"] = [front_image_url]  #中间件使用的格式是列表
        # article_item["praise_nums"] = praise_nums
        # article_item["fav_nums"] = fav_nums
        # article_item["commont_nums"] =  commont_nums
        # article_item["tags"] = tags
        # article_item["content"] = content



        front_image_url = response.meta.get("front_image_url", "")  #文章封面图的地址
        #通过itemloader加载item
        item_loader = ArticleItemLoader(item=JobBoleArticleItem(),response=response)

        item_loader.add_css("title",".entry-header h1::text")
        item_loader.add_css('create_date', 'p.entry-meta-hide-on-mobile::text')
        item_loader.add_value("url",response.url)
        item_loader.add_value("url_object_id",common.get_md5(response.url))
        item_loader.add_value("front_image_url",[front_image_url])
        item_loader.add_css("praise_nums",".vote-post-up h10::text")
        item_loader.add_css("comment_nums","a[href='#article-comment'] span::text")
        item_loader.add_css("fav_nums",".bookmark-btn::text")
        item_loader.add_css("tags","p.entry-meta-hide-on-mobile a::text")
        item_loader.add_css("content","div.entry")

        article_item = item_loader.load_item()


        yield article_item

