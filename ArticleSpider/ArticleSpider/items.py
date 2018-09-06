# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose,TakeFirst,Join

from datetime import datetime
import re

class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def add_jobbole(value):
    return value + "jobbole"


def date_convert(value):

    create_date = value.strip().replace('·','').strip()
    #字符串转换日期
    try:
        create_date = datetime.strptime(create_date,"%Y/%m/%d").date()
    except Exception as e :
        create_date = datetime.now().date()

    return create_date

def get_nums(value):
    match_re = re.match(r".*?(\d+).*",value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums


def remove_comment_tags(value):
    #去掉tag中提取的评论
    if '评论' in value:
        return ""
    else:
        return value


def return_value(value):
    """
    do nothing, 只是为了覆盖 ItemLoader 中的 default_processor
    """
    return value



class ArticleItemLoader(ItemLoader):
    #继承自定义itemloader
    default_output_processor = TakeFirst()  #默认所有item取第一个元素


class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field(
        input_processor=MapCompose(add_jobbole)
    )
    create_date = scrapy.Field(
        input_processor = MapCompose(date_convert)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()

    front_image_url = scrapy.Field(
        # 列表经过 默认 output_processor 是 TakeFirst()，这样front_image_url一个字符串，不是 list
        output_processor=MapCompose(return_value) #img pipeline 需要的是列表数据
    )
    front_image_path = scrapy.Field()

    praise_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )

    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        output_processor = Join(",")
    )
    content = scrapy.Field(
        # content 不是取最后一个，是全部都要，所以不用 TakeFirst()
        output_processor= Join("")
    )





