#!/usr/local/bin/python3
# -*- coding=utf8 -*-

import markdown
import sys
from jinja2 import Environment, PackageLoader, select_autoescape
import os
import shutil
import json
import time

config_directories = ['../config.json', 'config.json']
root_directory = os.path.split(
        os.path.split(
            os.path.realpath(sys.argv[0])
        )[0])[0]
templates_list = []
env = Environment(
        loader=PackageLoader('main', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

class Config:
    def __init__(self, dict):
        self.output_directory = dict['output_directory']
        self.template_directory = dict['template_directory']
        self.archives_directory = dict['archives_directory']
        self.css_directory = dict['css_directory']
        self.js_directory = dict['js_directory']
        self.blog_title = dict['blog_title']
        self.archive_output_directory = dict['archive_output_directory']
        self.img_directory = dict['img_directory']
        self.index_picture_light = dict['index_picture_light']
        self.index_picture_dark = dict['index_picture_dark']
        self.archives_order_by = dict['archives_order_by']
        self.date_format_string = dict['date_format_string']

# all the path is flitered by os.path.realpath(path, root_directory)
class Archive:
    def __init__(self, dict):
        self.href = dict['href']
        self.meta = dict['meta']
        self.text = dict['text']
        self.filename = dict['filename']
        self.html = dict['html']

class ArchivePair:
    def __init__(self, archive, sec):
        self.archive = archive
        self.sec = sec

def read_config():
    for config_path in config_directories:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                res = Config(json_data)
                return res
    return None


def path_transform(path):
    return os.path.join(root_directory, path)
    
def process_archives(config):
    res = []
    archives_directory = path_transform(config.archives_directory)
    archive_output_directory = path_transform(config.archive_output_directory)
    for filename in os.listdir(archives_directory):
        filepath = os.path.join(archives_directory, filename)
        
        # if find directories
        # copy to output directory
        if os.path.isdir(filepath):
            target_path = os.path.join(archive_output_directory, filename)
            # if target directory does not exist
            # then create one
            if not os.path.exists(target_path):
                os.makedirs(target_path)
            
            # copy the content of the source directory to the target directory
            if os.path.exists(target_path):
                for root, dirs, files in os.walk(filepath):
                    for file in files:
                        src = os.path.join(filepath, file)
                        shutil.copy(src, target_path)

        else:
            prefix = os.path.splitext(filename)[0]
            suffix = os.path.splitext(filename)[1]

            # markdown file
            if suffix == '.md':
                res_dir = {}
                res_dir['href'] = os.path.relpath(
                    os.path.join(archive_output_directory, prefix + ".html")
                )
                res_dir['filename'] = filename
                with open(filepath, 'r', encoding='utf-8') as f:
                    res_dir['text'] = f.read()

                md = markdown.Markdown(extensions=[
                    'toc', 'custom-span-class', 'meta'
                ])
                html = md.convert(res_dir['text'])
                res_dir['html'] = html
                res_dir['meta'] = md.Meta
                
                res.append(Archive(res_dir))

    return res
                

def init_templates(template_directory):
    for template in os.listdir(template_directory):
        template_path = os.path.join(template_directory, template)
        templates_list.append(template_path)


# return the matched template for the filename
def match_template(filename, template_directory):
    for template in templates_list:
        prefix = os.path.splitext(filename)[0]
        template_prefix = os.path.splitext(os.path.basename(template))[0]

        if prefix == template_prefix:
            return template
    return os.path.join(template_directory, 'archive.html')
    

def render_archives(archives, config):
    template_directory = path_transform(config.template_directory)
    archive_output_directory = path_transform(config.archive_output_directory)

    for archive in archives:
        template = env.get_template(
            os.path.relpath(
                match_template(archive.filename, template_directory),
                template_directory 
            )
        )
        html = template.render(archive=archive)
        basename = os.path.splitext(archive.filename)[0]
        target_filename = basename + ".html"

        with open(os.path.join(archive_output_directory, target_filename), 'w+', encoding='utf-8') as f:
            f.write(html)


def render_index(archives, config):
    blog_title = config.blog_title
    output_directory = path_transform(config.output_directory)
    img_directory = path_transform(config.img_directory)
    index_picture_light = config.index_picture_light

    

    archives_in_order = []
    
    for archive in archives:
        if config.archives_order_by == 'date':
            stime = time.strptime(archive.meta['date'][0], config.date_format_string)
            sec = time.mktime(stime)
            pair = ArchivePair(archive, sec)
            archives_in_order.append(pair)
    
    archives_in_order.sort(key=(lambda elem : elem.sec), reverse=True)
    archives_ = []

    for archive in archives_in_order:
        archives_.append(archive.archive)

    template = env.get_template("index.html")
    html = template.render(
        title=blog_title, 
        archives=archives_, 
        picture_path=os.path.relpath(
            path_transform(os.path.join(img_directory, index_picture_light))
        )
    )
    
    
    with open(os.path.join(output_directory, "index.html"), "w+", encoding='utf-8') as f:
        f.write(html)
    
        

if __name__ == '__main__':
    config = read_config()
    init_templates(path_transform(config.template_directory))

    archives = process_archives(config)

    render_archives(archives, config)

    render_index(archives, config)

