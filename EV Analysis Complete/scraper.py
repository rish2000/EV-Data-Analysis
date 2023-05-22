import requests
from bs4 import BeautifulSoup
import pandas as pd
import time


def scrapeEVData():
    #to concat extensions onto
    base_URL = 'https://ev-database.org'
    headers = requests.utils.default_headers()
    headers.update({
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
    })

    # proxies = { 'http': "http://159.223.149.216", 
    #         'https': "https://159.223.149.216"}

    #first scrape of all extensions
    initial_URL = "https://ev-database.org/#sort:path~type~order=.rank~number~desc|range-slider-range:prev~next=0~1200|range-slider-acceleration:prev~next=2~23|range-slider-topspeed:prev~next=110~350|range-slider-battery:prev~next=10~200|range-slider-towweight:prev~next=0~2500|range-slider-fastcharge:prev~next=0~1500|paging:currentPage=0|paging:number=all"
    page = requests.get(initial_URL)
    soup = BeautifulSoup(page.content, "html.parser")

    extension_list= []
    elem = soup.find_all('div', class_='img')
    for i in elem:
        href = i.find('a')['href']
        extension_list.append(href)

    extension_list = extension_list[0:316] #last two cars dont have data
    print('pulled initial data')

    final_data =[]
    for extension in extension_list:

        URL = base_URL + extension

        time.sleep(20)
        page = requests.get(URL)

        data = {}

        soup = BeautifulSoup(page.content, "html.parser")

        model = soup.find_all("h1")[0].string
        brand = model.split(' ')[0]
        print(model)

        data['Model'] = model
        data['Brand'] = brand

        results = soup.find(id= 'pricing')
        td_elements = results.find_all('td')
        prices= []
        for i in range(0, len(td_elements), 2):
            country_info = td_elements[i].text.strip()
            price_info = td_elements[i + 1].text.strip()

            if 'United Kingdom' in country_info and '£' in price_info:
                price_in_pounds = price_info.replace('£', '')
                data['Price_in_Pounds'] = price_in_pounds


        performance = soup.find(id= 'performance')
        tr_elems = performance.find_all('td')
        for i in range(0, len(tr_elems), 2):
            key = tr_elems[i].text.strip()
            metric = tr_elems[i + 1].text.strip()
            data[key] = metric

        battery = soup.find(id= 'battery')
        td_elems = battery.find_all('td')
        for i in range(0, len(td_elems), 2):
            key = td_elems[i].text.strip()
            metric = td_elems[i + 1].text.strip()
            data[key] = metric


        for i in range(0, len(td_elems), 2):
            key = td_elems[i].text.strip()
            if 'Time' in key:
                split = key.split()
                key = split[0] + ' ' + split[1]
            metric = td_elems[i + 1].text.strip()
            data[key] = metric

        efficiency = soup.find(id= 'efficiency')
        td_elems = efficiency.find_all('td')
        for i in range(0, len(td_elems), 2):
            key = td_elems[i].text.strip()
            metric = td_elems[i + 1].text.strip()
            data[key] = metric

        real_consumption = soup.find(id= 'real-consumption')
        td_elems = real_consumption.find_all('td')
        for i in range(0, len(td_elems), 2):
            key = td_elems[i].text.strip()
            metric = td_elems[i + 1].text.strip()
            data[key] = metric
        
        final_data.append(data)

    return final_data

if __name__ == '__main__':
    data = scrapeEVData()
    df = pd.DataFrame(data)
    df.to_csv('EVDataset.csv')
    print('done')