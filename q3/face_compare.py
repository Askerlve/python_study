# -*- coding: utf-8 -*-
import time
import traceback
import urllib2
import requests
import json
import csv
import os, os.path

import sys

reload(sys)
sys.setdefaultencoding('utf-8')


def pull_data(inventory, start_index, end_index):
    print(start_index, end_index)
    with open(inventory) as infile, open('face-compare-result-%s_%s.csv' % (start_index, end_index), 'w') as out_file:
        reader = csv.reader(infile)
        writer = csv.writer(out_file)
        writer.writerow(['applyId', 'userId', 'conf', 'isMatch', 'score', 'reviewed', 'response'])
        for idx, row in enumerate(reader):
            try:
                if idx < start_index or idx > end_index:
                    continue
                apply_uuid, apply_user_uuid = row[0], row[1]
                auth_image_url = get_image_url(apply_user_uuid, "AUTHORIZATION_PERSONAL")
                living_image_url = get_image_url(apply_user_uuid, "LIVING_BODY")
                auth_image_data = get_image_data(auth_image_url)
                living_image_data = get_image_data(living_image_url)
                headers = {"xx": "xx", "xx": "xx"}
                payload = {}
                files = {'selfie': ('auth_%s.jpg' % apply_user_uuid, auth_image_data, 'image/jpg'),
                         'id': ('living_%s.jpg' % apply_user_uuid, living_image_data, 'image/jpg')}
                response = requests.request("POST", "https://ind-faceid.hyperverge.co/v1/photo/verifyPair", headers=headers, data=payload, files=files)
                respStr = response.text
                result = json.loads(respStr)
                code = result['statusCode']
                if "200" == code:
                    conf = result['result']['conf']
                    match = result['result']['match']
                    score = result['result']['match-score']
                    reviewed = result['result']['to-be-reviewed']
                    writer.writerow([apply_uuid, apply_user_uuid, conf, match, score, reviewed, respStr])
                else:
                    writer.writerow([apply_uuid, apply_user_uuid, 0, 'no', 0, 'unknown', respStr])
            except Exception as e:
                writer.writerow([apply_uuid, apply_user_uuid, 0, 'no', 0, 'unknown', e.message])
                traceback.print_exc()
            time.sleep(0.5)


def get_image_data(image_url):
    response = urllib2.urlopen(image_url)
    return response.read()


def get_image_url(apply_user_uuid, image_type):
    url = 'http://localhost:9003/user/identification/report-data'
    data = {
        "userId": apply_user_uuid,
        "reportType": image_type,
    }
    header = {"Content-Type": "application/json"}
    response = requests.post(url, data=json.dumps(data), headers=header)
    result = json.loads(response.text)
    code = result['code']
    if "0" == code:
        return result['data']['imageUrl']
    else:
        raise Exception('获取图片地址异常,user_uuid:%s, result:%s' % (apply_user_uuid, result))


if __name__ == '__main__':
    print(sys.argv)
    # program, csv file, start index, end index
    if len(sys.argv) < 4:
        print("Miss required arguments!")
        sys.exit(1)

    in_file, start, end = sys.argv[1:]
    # print(os.path.abspath(in_file), start, end)
    pull_data(os.path.abspath(in_file), int(start), int(end))
