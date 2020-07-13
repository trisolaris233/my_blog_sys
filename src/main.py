#!/usr/local/bin/python3
# -*- coding=utf8 -*-

import markdown
import sys
from jinja2 import Environment, PackageLoader, select_autoescape
import os
import shutil
import json

config_directories = ['../config.json', 'config.json']
root_directory = os.path.split(
        os.path.split(
            os.path.realpath(sys.argv[0])
        )[0])[0]
templates_list = []

class Config:
    def __init__(self, dict):
        self.output_directory = dict['output_directory']
        self.template_directory = dict['template_directory']
        self.archives_directory = dict['archives_directory']
        self.css_directory = dict['css_directory']
        self.js_directory = dict['js_directory']

# all the path is flitered by os.path.realpath(path, root_directory)
class Archive:
    def __init__(self, dict):
        self.href = getattr(dict, 'href', "")
        self.meta = getattr(dict, 'meta', {})
        self.text = getattr(dict, 'text', "")
        self.filename = getattr(dict, 'filename')
        self.html = getattr(dict, 'html', "")


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
    
def process_archives(archives_directory, output_directory):
    res = []
    for filename in os.listdir(archives_directory):
        filepath = os.path.join(archives_directory, filename)
        
        # if find directories
        # copy to output directory
        if os.path.isdir(filepath):
            target_path = os.path.join(output_directory, filename)
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
                res_dir['href'] = filepath
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
    


if __name__ == '__main__':
    config = read_config()
    init_templates(path_transform(config.template_directory))
    
    archives = process_archives(
        path_transform(config.archives_directory),
        path_transform(config.output_directory)
    )

