import os
import sys
import csv
import time
import requests
import lxml.html
import re


base_url = "https://www.diyp.jp/room/"

if not os.path.exists('diyp_data.csv'):
    col_name = [
        'URL',
        '物件名称',
        '所在地',
        '最寄駅',
        '賃料',
        '管理費',
        '面積',
        '改装可能範囲',
        '原状回復',
        '敷金',
        '礼金',
        '条件',
        '築年',
        '構造規模',
        '契約内容',
        '備考',
        '情報掲載者',
        '取引容態',
        '募集有無',
        '最終確認日',
        'タイトル',
        '詳細'
    ]
    with open('diyp_data.csv', 'w') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(col_name)


def get_el(xpath, regex=None):
    try:
        if not regex:
            el = root.xpath(xpath)[0]
            el = re.sub(r'\s+', '', el)
            #print(el)
        else:
            el = root.xpath(xpath)[0].text_content()
            el = re.search(regex, el).group(1)
            el = re.sub(r'\s+', '', el)
            #print(el)
    except Exception as e:
        #print(e)
        el = ''
    return el


def get_el_shosai(xpath, regex):
    try:
        el = root.xpath(xpath)[0]
        el = lxml.html.tostring(el, method='html', encoding='utf-8').decode('utf-8')
        el = el.replace('\n', '')
        el = re.search(regex, el).group(1)
        el = el.replace('<br>', '').replace('<div id="description">', '')
        el = re.sub(r'\s+', '', el)
        #print(el)
    except Exception as e:
        #print(e)
        el = ''
    return el


def scrape(url):
    # GET DATA
    res = requests.get(url)
    global root
    root = lxml.html.fromstring(res.content)
    name = get_el('//*[@id="pc_headtitle"]/dl/dd[1]/text()')
    # No name = no page
    if not name:
        return
    address = get_el('//*[@id="pc_headtitle"]/dl/dd[2]/a/text()')
    station = get_el('//*[@id="pc_headtitle"]/dl/dd[3]/text()')
    chiryo = get_el('//*[@id="pc_headtitle"]/dl/dd[4]/span/text()')
    kanrihi = get_el('//*[@id="pc_headtitle"]/dl/dd[5]/span/text()')
    menseki = get_el('//*[@id="pc_headtitle"]/dl/dd[6]/span/text()')
    kaisoukanou = get_el('//*[@id="pc_headtitle"]/dl/dt[7]', r'改装可能範囲：\s*(\S+)')
    genzyokaihuku = get_el('//*[@id="pc_headtitle"]/dl/dt[8]', r'原状回復：\s*(\S+)')
    shikikin = get_el('//div[@id="description"]/p[2]', r'敷金：\s*(.*?)\s*礼金：')
    reikin = get_el('//div[@id="description"]/p[2]', r'礼金：\s*(.*?)\s*償却：')
    joken = get_el('//div[@id="description"]/p[3]', r'条件：\s*(\S+)')
    chikunen = get_el('//div[@id="description"]/p[5]', r'築年：\s*(.*?)\s*保険：')
    kozo = get_el('//div[@id="description"]/p[5]', r'構造規模：\s*(.*?)\s*契約内容：')
    keiyaku = get_el('//div[@id="description"]/p[5]', r'契約内容：\s*(.*?)\s*備考：')
    bikou =  get_el('//div[@id="description"]/p[5]', r'備考：\s*(\S+)')
    joho = get_el('//div[@id="description"]/p[6]', r'情報掲載者：\s*(.*?)\s*取引様態：')
    torihiki = get_el('//div[@id="description"]/p[6]', r'取引様態：\s*(.*?)\s*最終確認日：')
    boshu = get_el('//div[@id="room_end"]', r'(\S+)')
    saishu = get_el('//div[@id="description"]/p[6]', r'最終確認日：\s*(\S+)')
    title = get_el('//div[@id="room_images"]/h1/text()')
    shosai = get_el_shosai('//div[@id="description"]', r'^(.*?)<hr id=\"cc-section\">')

    data = [
        url,
        name,
        address,
        station,
        chiryo,
        kanrihi,
        menseki,
        kaisoukanou,
        genzyokaihuku,
        shikikin,
        reikin,
        joken,
        chikunen,
        kozo,
        keiyaku,
        bikou,
        joho,
        torihiki,
        boshu,
        saishu,
        title,
        shosai
    ]

    with open('diyp_data.csv', 'a') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(data)

cnt = 1
root = None

while cnt <= 2193:
    url = base_url + str(cnt)
    print(url)
    scrape(url)
    time.sleep(1)
    cnt += 50

print('DONE!!')
