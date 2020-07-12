#!/usr/local/bin/python3
# -*- coding=utf8 -*-

import markdown
import sys
from jinja2 import Environment, PackageLoader, select_autoescape
import os
import filetype



class Article:
    def __init__(self, url, title, text):
        self.url = url
        self.title = title 
        self.text = text

def scan_archives(path):
    res = []

    for file in os.listdir(path):
        print(file)
        if os.path.isdir(file):
            continue
        basename = os.path.basename(file)
        filename = os.path.splitext(basename)[0]
        suffix = os.path.splitext(basename)[1]

        if suffix == '.md':
            url = "../output/" + filename + ".html"
            title = filename
            text = ''
            
            with open(os.path.join(path, file), 'r') as f:
                text = f.read()

            res.append(Article(url, title, text))

    return res



if __name__ == '__main__':
    env = Environment(
        loader=PackageLoader('main', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('index.html')
    res = scan_archives("../archives")
    for archive in res:
        text = markdown.markdown(archive.text)
        with open(archive.url, 'w+') as f:
            f.write(text)


    html = template.render(
        picture_path='../test/sakura.png',
        title="sunshine+ice's blog", 
        articles=res
    )

    with open('index.html', 'w+') as f:
        f.write(html)

