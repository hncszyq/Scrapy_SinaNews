from SinaNews.items import SinanewsItem
from urllib.parse import urlencode 
import scrapy
import re 

class MySpider(scrapy.Spider):
    name = "MySpider"
    allowed_domains = ["sina.com.cn"]
    PageUrl = "https://feed.mix.sina.com.cn/api/roll/get?" 
    TotalPage = 1000    #需要爬取的总页数
    Params = {
        "pageid":"153",
        "lid":"2509",
        "k":"",
        "num":"50",
        "page":"",
        "r":"0.2738386476790582",
        "callback":"jQuery111206972270721486022_1566369517834",
        "_":"1566369517875",
    }
    finish = False

    def __init__(self):
        super(MySpider,self).__init__()
        self.PageCount = 1

    def start_requests(self):
        self.Params['page'] = str(self.PageCount)
        yield scrapy.Request(MySpider.PageUrl+urlencode(self.Params), callback = self.GetUrls)

    def GetUrls(self,response):    
        #获取一个页面的50个新闻链接
        urls = response.selector.re("\"urls\"\:\"\[\\\\\"(http.*?shtml)")
        for url in urls:
            url = re.sub("\\\\","",url)
            yield scrapy.Request(url,dont_filter=True)
        self.finish = True

    def SpecialPage(self,response,item):
        #创事记和苹果汇
        ###新闻标题
        item['title'] = response.xpath('//h1[@id="artibodyTitle"]//text()').extract()[0].replace("'","''").replace("\\","/")
        ###新闻日期
        item['date'] = response.xpath('//*[@id="pub_date"]//text()').extract()[0].strip()
        ###新闻编辑
        author = response.xpath('//*[@id="author_ename"]/a/text()').extract()
        if author:
            item['editor'] = author[0].strip()
        else:
            item['editor'] = "未知"
        ###新闻内容
        content = ''.join(response.xpath('//*[@id="artibody"]//p//text()').extract())
        try:
            #去广告
            ads = ''.join(response.xpath('//div[@id="artibody"]//div[@class="tech-quotation clearfix"]//p//text()').extract()).strip()
            content = content.replace(ads,'')
        finally:
            item['content'] = content.replace("'","''").replace("\\","/")    #避免标点符号引起的数据库错误 
        return item

    def FaWenPage(self,response,item):
        #法问
        ###新闻标题
        item['title'] = response.xpath('//h1[@class="m-atc-title"]//text()').extract()[0].replace("'","''").replace("\\","/")
        ###新闻日期
        item['date'] = response.xpath('//span[@class="atc-date"]//text()').extract()[0]
        ###新闻编辑
        item['editor'] = response.xpath('//span[@class="atc-author"]//text()').replace("作者：","")
        ###新闻内容
        item['content'] = ''.join(response.xpath('//div[@id="m_atc_original"]//p//text()').extract()).replace("'","''").replace("\\","/")
        return item

    def OldPage(self,response,item):
        #2018之前版本页面
        ###新闻标题
        item['title'] = response.xpath('//h1[@id="artibodyTitle" or @class="article-a__title" or @id="main_title"]//text()').extract()[0].replace("'","''").replace("\\","/")
        ###新闻日期
        item['date'] = re.findall("\d{4}[年-]{1}\d+[月-]{1}\d+[日]?[ ]*\d{2}:\d{2}:?\d{,2}",response.text)[0]
        ###新闻编辑
        item['editor'] = "未知"
        ###新闻内容
        item['content'] = ''.join(response.xpath('//div[@id="artibody"]//p//text()').extract()).replace("'","''").replace("\\","/")
        return item

    def CommonPage(self,response,item):
        #一般页面
        ###新闻标题
        item['title'] = response.xpath('//h1[@class="main-title"]//text()').extract()[0].replace("'","''").replace("\\","/")
        ###新闻日期
        item['date']  = response.xpath('//span[@class="date"]//text()').extract()[0]
        ###新闻编辑
        try:
            editor = response.xpath('//p[@class="article-editor" or @class="show_author"]//text()').extract()[0].strip()
            editor = re.sub("[(责任编辑：)a-zA-Z0-9]","",editor)
        except IndexError:
            editor = "未知"
        finally:
            item['editor'] = editor 
        ###新闻内容
        content = ''.join(response.xpath('//div[@id="artibody" or @id="article"]//p//text()').extract())
        try:
            #去免责声明
            #content = re.sub("本栏目所有文章.*?上述作品。","",content)
            #去无关文字
            content = re.sub("新浪军事：最多军迷首选的军事门户！","",content)
            #去编辑者
            ed = response.xpath('//p[@class="article-editor" or @class="show_author"]//text()').extract()[0].strip()
            content = content.replace(ed,'')
        except:
            pass
        try:
            #去广告
            ads = ''.join(response.xpath('//div[@id="artibody"]/div[@class="tech-quotation clearfix"]//p//text()').extract()).strip()
            content = content.replace(ads,'')
        finally:
            item['content'] = content.replace("'","''").replace("\\","/") 
        return item 

    def parse(self,response):
        item = SinanewsItem()
        #新闻链接
        item['url'] = response.url 
        try:
            if response.xpath('//h1[@class="main-title"]//text()').extract():
                #一般页面
                item = self.CommonPage(response,item)
            elif response.xpath('//*[@id="author_ename"]/a/text()'):
                #创事记或苹果汇
                item = self.SpecialPage(response,item)
            elif response.xpath('//h1[@class="m-atc-title"]//text()').extract():
                #法问
                item = self.FaWenPage(response,item)
            else:
                #2018之前版本
                item = self.OldPage(response,item)
            yield item
        except:
            if "/7x24/" in response.url:
                #7*24小时全球实时财经新闻直播
                pass
            elif "页面没有找到" in response.text:
                print("失效链接")
            else:
                print("异常链接：" + response.url)

        #继续下一页
        if self.finish and self.PageCount < MySpider.TotalPage:
            print(self.PageCount)
            self.finish = False
            self.PageCount += 1
            self.Params['page'] = str(self.PageCount)
            yield scrapy.Request(MySpider.PageUrl+urlencode(self.Params), callback = self.GetUrls, dont_filter = True) 
