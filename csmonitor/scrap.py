import requests
from bs4 import BeautifulSoup
import re

def write_file(file_name, data):
    with open(file_name, 'w+') as f:
        f.write(data)

def fetch(url : str):
    response = requests.get(url)
    return response.text
    # print(response.text)
    # write_file("test2.html", response.text)

def get_sectionid_and_section_title(html):
    soup = BeautifulSoup(html, "html.parser")
    ddp_item_link_href_tags = soup.select(".ddp-item-link-href")
    for tag in ddp_item_link_href_tags:
        data_ddp_toc_target = tag.get('data-ddp-toc-target')
        print(data_ddp_toc_target.replace('#', ''))
        print(tag.text.strip())




def parse_article_body(article):
    h_and_p_elements = []

    # 遍历文档的子元素
    for element in article.children:
        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']:
            h_and_p_elements.append(element)

    # 打印元素的文本内容，根据元素类型添加相应数量的 "#"
    for element in h_and_p_elements:
        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            # 获取标题级别并添加相应数量的 "#"
            heading_level = element.name[1:]
            hashes = '#' * int(heading_level)
            print(f"{hashes} {element.text}")
        else:
            print(element.text)




def parse_section(section):

    title = section.find('h2')
    print("TITLE>>>>>>>>>")
    if title:
        print(title.get_text())

    introduction = section.find("div", class_="editor-intro")
    print("INTRODUCTION>>>>>>>>>")
    if introduction:
        p_elements = introduction.find_all('p')
        paragraphs = [p.text for p in p_elements]
        print(paragraphs)

    quick_read = section.find("div", attrs={"data-widget-name": "ddp-item-mini"})
    print("QUICK_READ>>>>>>>>>>>")
    if quick_read:
        p_elements = quick_read.find_all('p')
        paragraphs = [p.text for p in p_elements]
        print(paragraphs)

    deep_read = section.find("article", attrs={"data-widget-name": "ddp-item-body"})
    print("DEEP_READ>>>>>>>>")
    if deep_read:
        body = deep_read.find("div", class_="eza-body")
        # p_elements = deep_read.find_all('p')
        # paragraphs = [p.text for p in p_elements]
        # print(paragraphs)
        parse_article_body(body)

def get_all_section(html):
    soup = BeautifulSoup(html, "html.parser")
    sections = soup.find_all('section', attrs={'id': re.compile(r'^\d+$')})
    for section in sections:
        print(section.get('id'))
        # print(section.text)  # 打印每个 section 的文本内容
        parse_section(section)

def main():
    url1 = 'https://www.csmonitor.com/Daily/2023/20231103'
    html = fetch(url1)
    get_all_section(html)

if __name__ == '__main__':
    main()
