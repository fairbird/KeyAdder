#!/usr/bin/python
# -*- coding: utf-8 -*-
from distutils.core import setup

PLUGIN_DIR = 'Extensions.KeyAdder'

setup(name='enigma2-plugin-extensions-KeyAdder',
       version='1.0',
       author='RAED',
       author_email='rrrr53@hotmail.com',
       description='plugin to Add and edit keys for (Biss, PowerVU, Irdeto and Tandberg).',
       packages=[PLUGIN_DIR],
       package_dir={PLUGIN_DIR: 'usr'},
       package_data={PLUGIN_DIR: ['plugin.png', '*/*.png']},
      )
