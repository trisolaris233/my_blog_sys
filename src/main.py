#!/usr/local/bin/python3
# -*- coding=utf8 -*-

import markdown
import sys
from jinja2 import Environment, PackageLoader, select_autoescape
import os
import shutil



class Article:
    def __init__(self, url, title, text, relative_url):
        self.url = url
        self.title = title 
        self.text = text
        self.relative_url = relative_url

def scan_archives(path, output_path, relative_output_path):
    res = []

    for file in os.listdir(path):
        print(file)
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            target_path = os.path.join(output_path, file)
            print(target_path)
            if not os.path.exists(target_path):
                os.makedirs(target_path)
            
            if os.path.exists(target_path):
                for root, dirs, files in os.walk(file_path):
                    for single in files:
                        src = os.path.join(root, single)
                        shutil.copy(src, target_path)

        basename = os.path.basename(file)
        filename = os.path.splitext(basename)[0]
        suffix = os.path.splitext(basename)[1]

        if suffix == '.md':
            url = os.path.join(output_path, filename + ".html")
            relative_url = os.path.join(relative_output_path, filename + ".html")
            title = filename
            text = ''
            
            with open(os.path.join(path, file), 'r') as f:
                text = f.read()

            res.append(Article(url, title, text, relative_url))

    return res



if __name__ == '__main__':
    env = Environment(
        loader=PackageLoader('main', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    index_template = env.get_template('index.html')
    page_template = env.get_template('archive.html')

    res = scan_archives("../archives", "../output", "output")
    for archive in res:
        md = markdown.Markdown(
            extensions=['meta', 'markdown_del_ins', 'custom-span-class']
        )
        text = md.convert(archive.text)
        
        
        try:
            title = md.Meta['title'][0]
        except:
            title = archive.title

        archive_html = page_template.render(
            title=title,
            body=text
        )
        with open("../output/" + archive.title + ".html", 'w+') as f:
            f.write(archive_html)


    html = index_template.render(
        picture_path='test/sakura.png',
        title="sunshine+ice's blog", 
        articles=res
    )

    with open('../index.html', 'w+') as f:
        f.write(html)

