# -*- coding: utf-8 -*-
# author: itimor

import requests
import json
from datetime import datetime, timedelta
import logging


def initlog(logfile):
    """
    创建日志实例
    """
    logger = logging.getLogger()
    hdlr = logging.FileHandler(logfile, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.WARNING)
    return logger


def diffdns(alldomains):
    domains = json.loads(requests.get(alldomains).text)
    for domain in domains:
        d = datetime.now()
        d10 = d - timedelta(minutes=10)
        cur_date = '{}-{}-{}'.format(d.year, d.month, d.day)
        cur_time = '{}:{}:{}'.format(d.hour, d.minute, d.second)
        create_time = '{}:{}:{}'.format(d10.hour, d10.minute, d10.second)
        uu = 'http://118.193.136.206:8000/api/domainstatus/?domain={}&create_time_0={}&create_time_1={}'.format(domain, cur_date, create_time, cur_time)
        # uu = 'http://118.193.136.206:8000/api/domainstatus/?domain={}'.format(domain)
        urlinfos = json.loads(requests.get(uu).text)
        if not len(urlinfos):
            logging.error("收集的状态记录为空")
            break

        ss = []
        ee = []
        for info in urlinfos:
            if info['status']:
                ss.append(info['node'])
            else:
                ee.append(info['node'])
        result = dict()
        result['node_count'] = len(urlinfos)
        result['error_node'] = ee
        result['url'] = domain

        if len(ss) > result['node_count'] / 2:
            result['status'] = True
        else:
            result['status'] = False

            # 自动切换ip
            # record_url = 'http://oms.tb-gaming.local/api/dnsrecords/'
            record_url = 'http://127.0.0.1:8000/api/dnsrecords/'

            x = domain.split('.')
            domainname = '{}.{}'.format(x[1], x[2])
            recordname = x[0]

            recorddata = json.loads(
                requests.get('{}?domain__name={}&name={}'.format(record_url, domainname, recordname)).text)[0]

            if recorddata['value2']:
                recorddata['value'], recorddata['value2'] = recorddata['value2'], recorddata['value']
                put_url = '{}{}/'.format(record_url, recorddata['id'])
                requests.put(put_url, data=recorddata)
                logging.warning("%s - ip已经自动更换 - %s" % (domain, result))
            else:
                logging.error("%s - 没有设置备用ip - %s" % (domain, result))
    return


if __name__ == '__main__':
    alldomains = 'http://118.193.136.206:8000/api/alldomains/'
    initlog('../logs/tan.log')
    print(diffdns(alldomains))
