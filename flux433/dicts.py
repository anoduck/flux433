#!/usr/bine/env python3
# -*- coding: utf-8 -*-
# MIT License = 'Copyright (c) 2024 Anoduck'
# This software is released under the MIT License.
# https: //opensource.org/licenses/MIT

class ParseDicts:

    def list_of_dicts(self, label, label_data, log):
        self.log = log
        self.log.info(label_data)
        self.log.info(f'Label Data is type: {type(label_data)}')
        ret_val = ''
        num_rows = len(label_data)
        if num_rows > 1:
            instance = label_data[0]
            if isinstance(instance, dict):
                row_list = []
                row_count = 0
                # Consume one list per turn
                for row in label_data:
                    entry_list = ''
                    # convert list of dicts to a list of strings
                    for key, value in row.items():
                        data = str(f'{key}="{value}"')
                        entry_list += ',' + data
                    if entry_list.startswith(','):
                        entry_list = entry_list[1:]
                    row_id = str(f'row_id="row{row_count}"')
                    list_entry = str(f'{row_id},{entry_list}')
                    if list_entry not in row_list:
                        row_list.append(list_entry)
                    row_count += 1
                ret_val += str(row_list)
                ret_val = ret_val.replace(" ", "")
            elif isinstance(instance, str):
                self.log.info(f'Single row string for {label} is {label_data}')
                ret_val = str(f'{label}="{label_data}"')
                ret_val = ret_val.replace(" ", "")
        if num_rows == 1:
            entry_list = ''
            rows = label_data[0]
            row_type = type(rows)
            self.log.info(f'Rows type is {row_type}')
            if isinstance(rows, dict):
                self.log.info(f'Single row dict for {label} is {rows}')
                for key, value in rows.items():
                    data = str(f'{key}="{value}"')
                    entry_list += ',' + data
                if entry_list.startswith(','):
                    entry_list = entry_list[1:]
                ret_val += ',' + str(entry_list)
            elif isinstance(rows, str):
                self.log.info(f'Single row string for {label} is {rows}')
                ret_val = str(f'{label}="{rows}"')
                ret_val = ret_val.replace(" ", "")
            else:
                self.log.info(f'Could not process {label} {rows}')
        if isinstance(ret_val, list):
            self.log.info(f'List of dicts returned {ret_val} as list')
            return str(ret_val)
        elif isinstance(ret_val, str):
            if ret_val.startswith(','):
                ret_val = ret_val[1:]
            self.log.info(f'List of dicts returned {ret_val} as string')
            return ret_val
        else:
            self.log.info(f'Could not process {label} {label_data}')
