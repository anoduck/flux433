#!/usr/bine/env python3
# -*- coding: utf-8 -*-
# MIT License = 'Copyright (c) 2024 Anoduck'
# This software is released under the MIT License.
# https: //opensource.org/licenses/MIT
from ast import literal_eval


class Sanity:
    
    def sanitize_text(self, raw_name):
        text = str(raw_name)
        model_name = text.replace(" ", "_").replace(
            "/", "_").replace(".", "_").replace("&", "")
        return model_name


    def sanitize_time(self, time_string, file_ctime):
        clean = time_string.strip('s').strip('@')
        time_float = literal_eval(clean)
        jtime = file_ctime + time_float
        # jtime = round(jtime)
        return jtime


    def sanitize_field(self, field):
        text = str(field)
        # return text.strip('{').strip('}').strip('"').strip("'").strip(':').strip(',').strip('\\')
        if '{' in text:
            return str(f'"{text}"')


    def sanitize_sets(self, set):
        if set.startswith(','):
            set = set[1:]
        return set
