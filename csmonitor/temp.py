import os
import re
import logging
import argparse
import requests
from bs4 import BeautifulSoup
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

def format_content(content):
    content_cleaned = [s.strip() + '\n\n' for s in content]
    formatted_content = ''.join(content_cleaned)
    return formatted_content

def fetch(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()  # 如果状态码不是2xx，将引发异常
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch URL: {url}")
        logger.error(e)
        return None

def parse_article_body(article):
    h_and_p_elements = []
    result = []

    for element in article.children:
        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']:
            h_and_p_elements.append(element)

    for element in h_and_p_elements:
        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            heading_level = element.name[1:]
            hashes = '#' * int(heading_level)
            result.append(f"{hashes} {element.get_text()}")
        else:
            result.append(element.get_text())

    return result

def parse_section(section):
    result = []
    title = section.find('h2')
    if title:
        logger.info(title)
        result.append('# ' + title.get_text().strip())



    introduction = section.find("div", class_="editor-intro")
    if introduction:
        p_elements = introduction.find_all('p')
        paragraphs = [p.get_text() for p in p_elements]
        # result.append("\n")
        result.append("### INTRODUCTION")
        # result.append("\n")
        result.extend(paragraphs)

    quick_read = section.find("div", attrs={"data-widget-name": "ddp-item-mini"})
    if quick_read:
        p_elements = quick_read.find_all('p')
        paragraphs = [p.get_text() for p in p_elements]
        # result.append("\n")
        result.append("### QUICK READ")
        # result.append("\n")
        result.extend(paragraphs)

    deep_read = section.find("article", attrs={"data-widget-name": "ddp-item-body"})
    if deep_read:
        body = deep_read.find("div", class_="eza-body")
        # result.append("\n")
        result.append("### DEEP_READ")
        # result.append("\n")
        result.extend(parse_article_body(body))

    return result

def parse_sections(sections):
    if sections:
        result = []
        for section in sections:
            logger.info(section.get('id'))
            result.extend(parse_section(section))
        return result
    return None

def get_all_sections(html):
    if html:
        soup = BeautifulSoup(html, "html.parser")
        sections = soup.find_all('section', attrs={'id': re.compile(r'^\d+$')})
        return sections
    return None

def parse_arguments():
    parser = argparse.ArgumentParser(description='Scrap the Christian Science Monitor Daily for a specific date')

    # 使用当前日期作为默认值
    default_date = datetime.today().strftime('%Y%m%d')

    parser.add_argument('--date', nargs='?', default=default_date, help='Date in YYYYMMDD format (default: today)')
    parser.add_argument('--path', default='./', help='Directory path for the output file')
    return parser.parse_args()

def main():

    args = parse_arguments()

    url = f'https://www.csmonitor.com/Daily/{args.date[0:4]}/{args.date}'
    logger.info(url)

    html = fetch(url)
    sections = get_all_sections(html)
    content = parse_sections(sections)
    if content:
        formatted_content = format_content(content)
        output_file_full_name = os.path.join(args.path, args.date + '.md')
        with open(output_file_full_name, 'w+', encoding='utf-8') as output_file:
            output_file.writelines(formatted_content)

if __name__ == '__main__':
    main()
