from json import dumps
from os import listdir, getcwd
from time import sleep
from urllib.parse import unquote

import requests as r
from lxml import etree

token = ':'
source_group = ''
bot = 'https://api.telegram.org/bot{}/'.format(token)
group_id = 0
preaching_room = 0
proxies = {
    'http': 'http://54.156.164.61:80',
    'https': 'https://35.233.136.146:3128'
}


def log(text):
    print(text)
    f = 10
    while f:
        try:
            r.post(bot + 'sendMessage', params={'chat_id': preaching_room, 'text': text}, proxies=proxies)
            f = 0
        except:
            f -= 1


def outp(elem, depth=0, index=''):
    print('\t' * depth, index, elem.tag, elem.attrib, repr(elem.text), repr(elem.tail))
    a = 0
    for sub in elem:
        outp(sub, depth + 1, index + ('.' if index else '') + str(a))
        a += 1


def post_post(link, text, photos):
    caption = '\n'.join(
        ['<a href="{}">{}</a>'.format(p[1], p[0]) if p[1] else p[0] for p in text]) + '\n\nSource: ' + link
    if len(photos) == 1:
        f = True
        while f:
            try:
                a = r.post(bot + 'sendPhoto',
                           params={'chat_id': group_id, 'caption': caption, 'parse_mode': 'HTML', 'photo': photos[0]},
                           proxies=proxies)
                f = False
                log(a.text)
            except:
                pass
    else:
        dicks = [{'type': 'photo', 'media': photo} for photo in photos]
        dicks[0]['caption'] = caption
        dicks[0]['parse_mode'] = 'HTML'
        f = True
        while f:
            try:
                a = r.post(bot + 'sendMediaGroup', params={'chat_id': group_id, 'media': dumps(dicks)}, proxies=proxies)
                f = False
                log(a.text)
            except:
                pass


def parse_post(post):
    post_link = 'https://vk.com/wall-' + post[0].attrib['name'].split('-')[-1]
    txt = []
    for tag in post[-1][0]:
        text = tag.text
        link = None
        if tag.tag == 'a' and text and text[0] != '#':
            link = tag.attrib['href']
            if link[0] == '/':
                link = 'https://vk.com' + link
            if 'vk.com/away.php' in link:
                link = unquote(link.split('=')[1].split('&')[0])
            if text == link:
                link = None
        if text:
            text = text.strip()
            if text:
                txt.append((text, link))
        tail = tag.tail
        if tail:
            tail = tail.strip()
            if tail:
                txt.append((tail, None))
    photos = []
    for a in post[-1][1][0][0][0][0]:
        f = True
        while f:
            try:
                photos.append(
                    etree.fromstring(r.get('https://vk.com' + a.attrib['href'].split('?')[0]).text, etree.HTMLParser())[
                        1][0][1][1][0][2][0][0][0][0][0].attrib['src'])
                f = False
            except:
                pass
    post_post(post_link, txt, photos)


def refresh(last_post_no):
    f = True
    while f:
        try:
            req = r.get(source_group)
            f = False
            posts = etree.fromstring(req.text, etree.HTMLParser())[1][0][1][1][0][2][0][-1]
            for post in posts[::-1]:
                if post.attrib['class'] == 'wall_item':
                    n = int(post[0].attrib['name'].split('_')[-1])
                    log('Found post ' + str(n))
                    if n > last_post_no:
                        log('Parsing...')
                        parse_post(post)
                        last_post_no = n
                    else:
                        log('Skipping because the last processed post was ' + str(last_post_no))
            return last_post_no
        except:
            pass


if 'last.txt' not in listdir(getcwd()):
    with open('last.txt', 'w') as o:
        o.write('0')
with open('last.txt') as o:
    N = int(o.read().strip())
while True:
    N = refresh(N)
    with open('last.txt', 'w') as o:
        o.write(str(N))
    for i in range(1800, 0, -1):
        print(i)
        sleep(1)
