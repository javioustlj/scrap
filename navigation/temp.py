import requests
import yaml
from bs4 import BeautifulSoup

# 发送 HTTP 请求并获取页面内容
def get_page(url):
    response = requests.get(url)
    return response.text

# 解析页面内容，提取导航数据
def parse_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    nav_items = soup.find_all('div', class_='nav-item')
    nav_data = []
    
    for nav_item in nav_items:
        taxonomy = nav_item.find('h3').text.strip()
        icon = nav_item.find('i').get('class')[1]
        links = []
        
        link_items = nav_item.find_all('div', class_='nav-link')
        
        for link_item in link_items:
            link = {}
            link['title'] = link_item.find('a').text.strip()
            link['logo'] = link_item.find('img')['src']
            link['url'] = link_item.find('a')['href']
            link['description'] = link_item.find('p').text.strip()
            links.append(link)
        
        nav_data.append({
            'taxonomy': taxonomy,
            'icon': icon,
            'links': links
        })
    
    return nav_data

# 将导航数据输出为 YAML 格式
def output_yaml(data):
    yaml_data = yaml.dump(data, allow_unicode=True)
    print(yaml_data)

# 主函数
def main():
    url = 'https://nav.bahuangshanren.tech/'
    html = get_page(url)
    nav_data = parse_page(html)
    output_yaml(nav_data)

# 执行主函数
if __name__ == '__main__':
    main()
