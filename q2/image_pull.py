# -*- coding: utf-8 -*-
import traceback
import urllib2
import requests
import json
import csv
import os, os.path

import sys

reload(sys)
sys.setdefaultencoding('utf-8')


def pull_data(inventory, start_index, end_index, report_type):
    print(start_index, end_index, report_type)
    with open(inventory) as infile:
        reader = csv.reader(infile)
        for idx, row in enumerate(reader):
            if idx < start_index or idx > end_index:
                continue
            apply_uuid, apply_user_uuid = row[0], row[1]

            url = 'http://localhost:9003/user/identification/report-data'
            data = {
                "userId": apply_user_uuid,
                "reportType": report_type,
            }
            header = {"Content-Type": "application/json"}
            response = requests.post(url, data=json.dumps(data), headers=header)
            result = json.loads(response.text)
            code = result['code']
            if ("0" == code):
                image_url = result['data']['imageUrl']
                print(image_url)
                save_img(image_url, apply_user_uuid, report_type)
            else:
                print(result)

def save_img(img_url, apply_user_uuid, report_type):
    print(img_url, apply_user_uuid, report_type)
    try:
        if not os.path.exists(report_type):
            print('文件夹', report_type, '不存在，重新建立')
            os.makedirs(report_type)
        # 获得图片后缀
        if 'jpeg' in img_url:
            file_suffix = '.jpeg'
        elif 'jpg' in img_url:
            file_suffix = '.jpg'
        elif 'png' in img_url:
            file_suffix = '.png'
        else:
            file_suffix = '.jpeg'
        # 拼接图片名（包含路径）
        filename = '{}_{}{}'.format(report_type, apply_user_uuid, file_suffix)
        print('filename:' + filename)
        # 下载图片，并保存到文件夹中
        response = urllib2.urlopen(img_url)
        cat_img = response.read()
        with open(report_type + '/' + filename, 'wb') as f:
            f.write(cat_img)
    except Exception as e:
        traceback.print_exc()


if __name__ == '__main__':
    print(sys.argv)
    # program, csv file, start index, end index
    if len(sys.argv) < 4:
        print("Miss required arguments!")
        sys.exit(1)

    in_file, start, end, report_type = sys.argv[1:]
    # print(os.path.abspath(in_file), start, end)
    pull_data(os.path.abspath(in_file), int(start), int(end), report_type)
