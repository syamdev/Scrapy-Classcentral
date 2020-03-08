# -*- coding: utf-8 -*-
from scrapy import Spider
from scrapy.http import Request


class ClasscentralSpider(Spider):
    name = 'classcentral'
    allowed_domains = ['classcentral.com']
    start_urls = ['https://www.classcentral.com/subjects']

    def __init__(self, subject=None):
        self.subject = subject

    def parse(self, response):
        if self.subject:
            subject_url = response.xpath('//a[contains(@title, "' + self.subject + '")]/@href').extract_first()
            absolute_subject_url = response.urljoin(subject_url)
            yield Request(absolute_subject_url,
                          callback=self.parse_subject)
        else:
            subjects = response.xpath('//h3/a[1]/@href').extract()
            for subject in subjects:
                absolute_subject_url = response.urljoin(subject)
                yield Request(absolute_subject_url,
                              callback=self.parse_subject)

    def parse_subject(self, response):
        subject_name = response.xpath('//h1/text()').extract_first()
        courses = response.xpath('//tr[@itemtype="http://schema.org/Event"]')

        for course in courses:
            course_name = course.xpath('.//*[@itemprop="name"]/text()').extract_first().strip()
            course_url = course.xpath('.//a[@itemprop="url"]/@href').extract_first()
            absolute_course_url = response.urljoin(course_url)

            yield Request(absolute_course_url,
                          callback=self.parse_course,
                          meta={'subject_name': subject_name,
                                'course_name': course_name,
                                'absolute_course_url': absolute_course_url})

        next_page = response.xpath('//link[@rel="next"]/@href').extract_first()
        if next_page:
            absolute_next_page = response.urljoin(next_page)

            yield Request(absolute_next_page,
                          callback=self.parse_subject)

    def parse_course(self, response):
        subject_name = response.meta['subject_name']
        course_name = response.meta['course_name']
        absolute_course_url = response.meta['absolute_course_url']
        ins_pro = response.xpath('//p[@class="text-1 block large-up-inline-block z-high relative"]')
        institution = ins_pro.xpath('.//a[@class="color-charcoal"]/text()').extract_first()
        provider = ins_pro.xpath('.//a[@class="color-charcoal italic"]/text()').extract_first()
        bookmark = response.xpath('//strong[@class="text-3 weight-semi inline-block"]/text()').extract_first()
        found_in = ', '.join(response.xpath('//span[@class="inline-block margin-right-xxsmall"]/a/text()').extract())
        reviews = response.xpath('//strong[@class="text-1 weight-semi"]/text()')[1].extract()
        class_url = response.xpath('//a[@class="btn-green btn-large padding-horz-xxlarge"]/@href').extract_first()
        cost = response.xpath('//strong[@class="text-3 upper weight-semi width-1-3"][contains(text(), "Cost")]/following-sibling::span[@class="text-2 color-charcoal width-2-3 block"]/text()').extract_first().strip()
        language = response.xpath('//strong[@class="text-3 upper weight-semi width-1-3"][contains(text(), "Language")]/following-sibling::a[@class="text-2 color-charcoal width-2-3 block"]/text()').extract_first().strip()
        certificate = response.xpath('//strong[@class="text-3 upper weight-semi width-1-3"][contains(text(), "Certificate")]/following-sibling::span/text()').extract_first('').strip() or 'N/A'
        paragraph_list = response.xpath('//div[@data-expand-article-target="overview"]/text()').extract()
        overview = ''.join(line.rstrip("\n") for line in paragraph_list).strip()

        yield {'subject_name': subject_name,
               'course_name': course_name,
               'absolute_course_url': absolute_course_url,
               'institution': institution,
               'provider': provider,
               'bookmark': bookmark,
               'found_in': found_in,
               'reviews': reviews,
               'class_url': class_url,
               'cost': cost,
               'language': language,
               'certificate': certificate,
               'overview': overview}
