#!/usr/bin/env python
#标识运行使用的当前环境的python解释器

"""
手动生成所有SKU静态html文件
"""
import sys
sys.path.insert(0,'../')

import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'

import django
django.setup()

from contents.crons import generate_static_index_html

if __name__ == '__main__':
    generate_static_index_html()




