#!/usr/local/bin/python3
# -*- coding=utf8 -*-

import markdown
import sys
import json


def read_config():
    with open("config.json", "r", encoding="utf-8") as config_file:
        config_content = config_file.read()
    config = json.loads(config_content)
    return config

class Config:
    def Config(self, dict_config):
        self.dict = dict_config
        self.page_directory = dict_config['page_directory']
        self.render_directory = dict_config['render_directories']
        self.use_template = dict_config['use_template']

class MarkdownText:
    def MarkdownText(self, markdown_text):
        self.text = markdown_text
        self.title = ""
        self.author = ""
        self.date = None
        self.last_update_date = None
        self.tag = []
        self.category = []

    def preprocess(self):
        pass

if __name__ == "__main__":
    print(sys.argv)

    with open(sys.argv[1], "r", encoding="utf-8") as input_file:
        t = input_file.read()
    print(t)
    html = markdown.markdown(t)
    print(html)
    with open(sys.argv[2], "w", encoding="utf-8") as output_file:
        output_file.write(html)

