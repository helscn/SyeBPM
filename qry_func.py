import requests
import re
import json
from os import path
from glob import iglob
from datetime import datetime, timedelta
from random import random

FUNCTION_NAMES = {
    '用户名': 'username',
    '密码': 'password',
    '型号': 'pn',
    '在制品': 'wip',
    '日期': 'date',
    '市场立项单': 'mkt',
    '立项单': 'mkt',
    '黑名单': 'hmd',
    '特殊型号': 'hmd',
    '偏差': 'pcd',
    '偏差单': 'pcd',
    '产品u单': 'cpud',
    'u单': 'gjud',
    '工具u单': 'gjud',
    '工具': 'gjud',
    '返工u单': 'fgud',
    '返工单': 'fgud',
    '返工': 'fgud',
    '黄卡': 'hk',
    '工艺建议书': 'ecn',
    '建议书': 'ecn',
    '联络单': 'lld',
    '文件': 'iso',
    '通告': 'ti',
    '东城值班': 'dczb',
    '值班': 'dczb',
    'npi查询': 'npi',
    '会议': 'meeting'
}


LOGIN_ERROR = [{
    'Title': 'BPM登陆错误，请确认账号密码是否有误！',
    'SubTitle': '可以使用 username 和 password 指令更新使用的账号名及密码。',
    'IcoPath': 'Images\\SYE.ico'
}]

QUERY_ERROR = [{
    'Title': '查询ERP时结果时出现错误！请检查网络是否有异常。',
    'IcoPath': 'Images\\SYE.ico'
}]

QUERY_EMPTY = [{
    'Title': '没有查到任何匹配结果，请检查关键词是否输入有误。',
    'IcoPath': 'Images\\SYE.ico'
}]

ACCOUNT = {
    'username': 'account',
    'password': 'password',
    'cookies': {}
}
CONFIG_FILE = '..\\account.json'
CONFIG_FILE = path.join(path.dirname(__file__), CONFIG_FILE)

try:
    # 读取账号配置文件
    with open(CONFIG_FILE, 'r') as f:
        ACCOUNT.update(json.load(f))
except Exception as e:
    raise e


def query_username(username):
    # 更新账号用户名
    if username.isnumeric() and len(username) >= 2:
        ACCOUNT['username'] = username
        with open(CONFIG_FILE, 'w') as f:
            json.dump(ACCOUNT, f, indent=2, sort_keys=True)
        return [{
            'Title': '用户账号已更新为：'+ACCOUNT['username'],
            'IcoPath': 'Images\\SYE.ico'
        }]
    else:
        return [{
            'Title': '请输入登陆BPM系统的用户账号名',
            'SubTitle': '当前用户名为：'+ACCOUNT['username'],
            'IcoPath': 'Images\\SYE.ico'
        }]


def query_password(password):
    # 更新账号密码
    if len(password) > 5:
        ACCOUNT['password'] = password
        with open(CONFIG_FILE, 'w') as f:
            json.dump(ACCOUNT, f, indent=2, sort_keys=True)
        return [{
            'Title': '用户密码已更新为：'+ACCOUNT['password'],
            'IcoPath': 'Images\\SYE.ico'
        }]
    else:
        return [{
            'Title': '请输入登陆BPM系统的用户密码',
            'SubTitle': '当前密码为：'+ACCOUNT['password'],
            'IcoPath': 'Images\\SYE.ico'
        }]


def get_cookies(url, data):
    # 登陆BPM系统获取Cookies
    session = requests.Session()
    res = session.post(url=url, data=data)
    cookies = requests.utils.dict_from_cookiejar(session.cookies)
    if '用户名或密码错误' in res.text:
        return None

    ACCOUNT['cookies'] = cookies
    with open(CONFIG_FILE, 'w') as f:
        json.dump(ACCOUNT, f, indent=2, sort_keys=True)
    return cookies


def get_url(url, params=None):
    # 使用保存的Cookies登陆获取指定接口数据
    res = requests.get(url=url, params=params, cookies=ACCOUNT['cookies'])
    if res.status_code != 200 or ('输入工号和密码' in res.text):
        cookies = get_cookies(
            url='http://eip.sye.com.cn:8181/bpm/login',
            data={
                'UserName': ACCOUNT['username'],
                'Password': ACCOUNT['password']
            }
        )
        res = requests.get(url=url, params=params, cookies=cookies)

    if '用户名或密码错误' in res.text or '输入工号和密码' in res.text:
        return None

    return res

def get_json(url, params=None):
    # 使用保存的Cookies登陆获取指定接口数据
    res = requests.get(url=url, params=params, cookies=ACCOUNT['cookies'])
    if res.status_code != 200 or ('输入工号和密码' in res.text):
        cookies = get_cookies(
            url='http://eip.sye.com.cn:8181/bpm/login',
            data={
                'UserName': ACCOUNT['username'],
                'Password': ACCOUNT['password']
            }
        )
        res = requests.get(url=url, params=params, cookies=cookies)

    if '用户名或密码错误' in res.text or '输入工号和密码' in res.text:
        return None

    return json.loads(res.text.replace('\t',''))



def query_pn(param):
    # 在生益ERP系统中查询料号型号名
    result = []
    if len(param) < 5:
        return [{
            'Title': '请输入需要查询的产品型号。',
            'IcoPath': 'Images\\SYE.ico'
        }]

    url = 'http://syeeip.sye.com.cn:8181/bpm/r?wf_num=R_SYE_B004&wf_gridnum=V_SYE_E001&wf_action=edit&wf_docunid=cc098b0f0d6d90449d0a9d409b3be042b578'
    payload = {
        'rdm': str(random()),
        'syxh': param.strip(),
        'company': '东莞'
    }
    r = requests.get(url, params=payload)
    try:
        if not r.text:
            return result
        for row in r.json()['rows']:
            pn = row['pdctno'].strip()
            result.append({
                'Title': pn,
                'SubTitle': row['custpno'],
                'IcoPath': 'Images\\SYE.ico',
                'ContextData': pn
            })
        if not result:
            return QUERY_EMPTY
        else:
            return result
    except Exception as e:
        return QUERY_ERROR


def query_wip(param):
    # 在生益ERP系统中根据料号名查询WIP
    result = []
    if len(param.strip()) < 5:
        return [{
            'Title': '请输入需要查询WIP的产品型号。',
            'IcoPath': 'Images\\SYE.ico'
        }]

    url = 'http://syeeip.sye.com.cn:8181/bpm/r?wf_num=R_SYE_B001&wf_gridnum=V_SYE_E002&wf_action=edit&wf_docunid=cc098b0f0d6d90449d0a9d409b3be042b578'
    pns = query_pn(param.strip())
    for row in pns:
        if row['Title'] == QUERY_EMPTY[0]['Title']:
            return pns
        pn = row['ContextData']
        payload = {
            'rdm': str(random()),
            'syxh': pn,
            'company': '东莞'
        }
        try:
            r = requests.get(url, params=payload)
        except Exception as e:
            return QUERY_ERROR
        if r.text:
            for process in r.json()['rows']:
                if process['wip']:
                    if process['scrapunit']:
                        scrapunit = '（已废{}单元）'.format(process['scrapunit'])
                    else:
                        scrapunit = ''
                    result.append({
                        'Title': process['pdctno'].strip(),
                        'SubTitle': '{0}{1}{2}{3}'.format(
                            process['techname'].strip().ljust(16),
                            process['wip'],
                            process['units'],
                            scrapunit
                        ),
                        'IcoPath': 'Images\\SYE.ico',
                        "ContextData": process['pdctno'].strip()
                    })
    if not result:
        result = QUERY_EMPTY.copy()
        result[0]['SubTitle'] = '未找到 {} 的WIP信息。'.format(param)
        return result
    else:
        return result


def context_wip(param):
    # 右键显示料号WIP的详细流程
    result = []
    url = 'http://syeeip.sye.com.cn:8181/bpm/r?wf_num=R_SYE_B001&wf_gridnum=V_SYE_E002&wf_action=edit&wf_docunid=80406cd90570c0412c092df076af5a9d98dc'
    pn = param.strip()
    payload = {
        'rdm': str(random()),
        'syxh': pn,
        'company': '东莞'
    }
    r = requests.get(url, params=payload)
    try:
        if r.text:
            for process in r.json()['rows']:
                if process['wip']:
                    units = process['wip']+process['units']
                else:
                    units = ''
                if process['scrapunit']:
                    scrapunit = '（已废{}单元）'.format(process['scrapunit'])
                else:
                    scrapunit = ''
                if units:
                    result.append({
                        'Title': process['techname'],
                        'SubTitle': units + scrapunit,
                        'IcoPath': 'Images\\SYE.ico'
                    })
                else:
                    result.append({
                        'Title': process['techname'],
                        'SubTitle': units + scrapunit,
                        'IcoPath': 'Images\\Blank.png'
                    })
        if not result:
            return QUERY_EMPTY
        else:
            return result
    except Exception as e:
        return QUERY_ERROR


def query_date(param):
    # 查询指定日期或指定天数前后的周期及星期
    param = param.strip().lower()
    d = datetime.today()
    oneday = timedelta(days=1)
    date_str = param.replace('.', '-').replace('/', '-')
    prefix = '今天'
    if param[:4] == 'yest':
        prefix = '昨天'
        d = d - oneday
    elif re.match('^-?\d+$', param):
        days_dif = int(param)
        if days_dif > 0:
            prefix = '{} 天后'.format(days_dif)
        elif days_dif < 0:
            prefix = '{} 天前'.format(abs(days_dif))
        d = d + oneday * int(param)
    elif re.match('^\d+-\d+-\d+$', date_str):
        prefix = '指定'
        d = datetime.strptime(date_str, '%Y-%m-%d')

    weekday_name = ['一', '二', '三', '四', '五', '六', '七']
    year, weeknum, weekday = d.isocalendar()
    weekday = weekday_name[weekday-1]
    return [{
        'Title': '{}日期：{} 年 {} 月 {} 日'.format(prefix, d.year, d.month, d.day),
        'SubTitle': '{} 年第 {} 周 星期{}'.format(year, weeknum, weekday),
        'IcoPath': 'Images\\Blank.png'
    }]


def query_dczb(param):
    # 在生益ERP系统中查询东城厂当天的值班信息
    result = []
    params = re.split(r'\s+', param.upper().strip())

    url = 'http://eip.sye.com.cn:8181/bpm/r?wf_num=R_PUB004_B006&wf_gridnum=V_PUB004_E002&wf_action=edit&wf_docunid=eea00c700e0ec049880abb20fb47e46ade79&rdm=' + \
        str(random())+'&factory=%E4%B8%9C%E5%9F%8E&sdate=%E4%BB%8A%E5%A4%A9&isSearch=true&page=1&rows=100'
    res = get_url(url)
    if res is None:
        return LOGIN_ERROR
    try:
        persons = res.json()
    except Exception as e:
        return QUERY_ERROR
    for person in persons['rows']:
        flag = True
        phone = ('📞'+person['phone']).ljust(30, ' ') if person['phone'] else ''
        tel = ('☎'+person['tel']) if person['tel'] else ''
        for param in params:
            if not(param in person['bc'] or param in person['name'] or param in person['zblx'] or param in person['user_dept'] or param in person['area'] or param in person['position']):
                flag = False
                break
        if flag:
            result.append({
                'Title': '[{}] {}'.format(person['bc'], person['name']).ljust(10, '　')+phone+tel,
                'SubTitle': '{}   {}   {}   {}'.format(person['zblx'], person['user_dept'], person['area'], person['position']),
                'IcoPath': 'Images\\Avatar.png'
            })
    if not result:
        result = QUERY_EMPTY.copy()
        result[0]['SubTitle'] = '未找到关键词包含 {} 的值班信息。'.format(param)
        return result
    else:
        return result


def query_meeting(param):
    result = []
    param = param.strip().replace('.', '-').replace('/', '-')
    url = 'http://eip.sye.com.cn:8181/bpm/r?wf_num=R_ADM004_B009&wf_gridnum=V_ADM004_E004&wf_action=edit&wf_docunid=0bc044020448904ecd08bf303064fb498b45&rdm=' + \
        str(random())
    try:
        data = get_json(url)
        if data is None:
            return LOGIN_ERROR
    except:
        return QUERY_ERROR

    for item in data['rows']:
        if param in item['usedate1'] or param in item['Subject'] or param in item['room']:
            result.append({
                'Title': '{} @ {}会议室'.format(item['Subject'],item['room']),
                'SubTitle': '{}  {} - {}'.format(item['usedate1'], item['starttime'], item['endtime']),
                'IcoPath': 'Images\\SYE.ico',
                "ContextData": item['WF_OrUnid'],
                'JsonRPCAction': {
                    'method': 'open_url',
                    'parameters': ['http://eip.sye.com.cn:8181/bpm/form?wf_num=F_ADM004_A007&wf_action=read&wf_docunid='+item['WF_OrUnid']]
                }
            })
    if not result:
        return QUERY_EMPTY
    else:
        result.sort(key=lambda v: v['SubTitle'])
        return result


def query_cpud(param):
    # 在生益ERP系统中根据料号名查询产品U单
    result = []
    param = param.strip()
    if len(param) < 5:
        return [{
            'Title': '请输入需要查询产品U单的产品型号。',
            'IcoPath': 'Images\\SYE.ico'
        }]

    url = 'http://eip.sye.com.cn:8181/bpm/r?wf_num=R_QA002_B034&wf_gridnum=V_QA002_G025&div=DC&search=true&rdm=' + \
        str(random())+'&chanpinxinghao='+param
    res = get_url(url)
    if res is None:
        return LOGIN_ERROR
    try:
        uds = res.json()
    except Exception as e:
        return QUERY_ERROR
    for ud in uds['rows']:
        result.append({
            'Title': ud['udanbianhao']+': '+ud['chanpinxinghao']+' 在 ' + ud['xuangongxu'] + ' 发现 ' + ud['quexianmingcheng'],
            'SubTitle': ud['WF_DocCreated'] + ' : ' + ud['quexianmiaoshu'],
            'IcoPath': 'Images\\SYE.ico',
            "ContextData": ud['udanbianhao'],
            'JsonRPCAction': {
                'method': 'open_url',
                'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B062&wf_docunid='+ud['WF_OrUnid']]
            }
        })
    if not result:
        result = QUERY_EMPTY.copy()
        result[0]['SubTitle'] = '未找到 {} 的产品U单。'.format(param)
        return result
    else:
        result.sort(key=lambda v: v['Title'], reverse=True)
        return result


def context_cpud(param):
    # 右键显示对应的产品U单内容
    result = []
    url = 'http://eip.sye.com.cn:8181/bpm/r?wf_num=R_QA002_B034&wf_gridnum=V_QA002_G025&div=DC&search=true&rdm=' + \
        str(random())+'&udanbianhao='+param
    res = get_url(url)
    if res is None:
        return LOGIN_ERROR
    try:
        uds = res.json()
    except Exception as e:
        return QUERY_ERROR
    for ud in uds['rows']:
        result.append({
            'Title': '产品型号：' + ud['chanpinxinghao'],
            'IcoPath': 'Images\\SYE.ico'
        })
        result.append({
            'Title': '工单编号：' + ud['gongdanhao3'],
            'IcoPath': 'Images\\SYE.ico'
        })
        result.append({
            'Title': '申请时间：' + ud['WF_DocCreated'],
            'IcoPath': 'Images\\Blank.png'
        })
        result.append({
            'Title': '开单工序：' + ud['xuangongxu'],
            'IcoPath': 'Images\\Blank.png'
        })
        result.append({
            'Title': '责任工序：' + ud['zerengognxu'],
            'IcoPath': 'Images\\Blank.png'
        })
        result.append({
            'Title': '缺陷数量：' + ud['buhegeshuliang'] + ' (批量总数：' + ud['piliang'] + ')',
            'IcoPath': 'Images\\Blank.png'
        })
        result.append({
            'Title': '缺陷名称：' + ud['quexianmingcheng'] + ' (' + ud['qxlb'] + ')',
            'IcoPath': 'Images\\Blank.png'
        })
        result.append({
            'Title': '缺陷描述：',
            'SubTitle': '　　'+ud['quexianmiaoshu'],
            'IcoPath': 'Images\\Blank.png'
        })
        result.append({
            'Title': '处理意见：',
            'SubTitle': '　　'+ud['qchuliyijian'],
            'IcoPath': 'Images\\Blank.png'
        })
        result.append({
            'Title': '返工方法：',
            'SubTitle': '　　'+ud['fangongfangfa'],
            'IcoPath': 'Images\\Blank.png'
        })
    return result

def query_bzud(param):
    # 在生益ERP系统中根据料号名查询背钻U单
    result = []
    param = param.strip()
    if len(param) < 5:
        return [{
            'Title': '请输入需要查询背钻U单的产品型号。',
            'IcoPath': 'Images\\SYE.ico'
        }]

    url = 'http://eip.sye.com.cn:8181/bpm/r?wf_num=R_QA001_B052&wf_gridnum=V_QA001_G015&wf_action=edit&wf_docunid=be05729f0c65704f5d08eb20b7767b09c83d&rdm=' + \
        str(random())+'&Status=ok&page=1&rows=25&udxh='+param
    
    res = get_url(url)
    if res is None:
        return LOGIN_ERROR
    try:
        uds = res.json()
    except Exception as e:
        return QUERY_ERROR
    for ud in uds['rows']:
        try:
            result.append({
                'Title': '{} ({})'.format(ud['Subject'],ud['quexianmiaoshu']),
                'SubTitle': '{} ({})'.format(ud['WF_DocCreated'],ud['WF_CurrentNodeName']),
                'IcoPath': 'Images\\SYE.ico',
                "ContextData": ud['WF_OrUnid'],
                'JsonRPCAction': {
                    'method': 'open_url',
                    'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B062&wf_docunid='+ud['WF_OrUnid']]
                }
            })  
        except Exception as e:
            return [{
                    'Title': '出现错误',
                    'IcoPath': 'Images\\SYE.ico'
                    }]
    if not result:
        result = QUERY_EMPTY.copy()
        result[0]['SubTitle'] = '未找到 {} 的背钻工具U单。'.format(param)
        return result
    else:
        result.sort(key=lambda v: v['SubTitle'], reverse=True)
        return result

def query_zkud(param):
    # 在生益ERP系统中根据料号名查询钻孔U单
    result = []
    param = param.strip()
    if len(param) < 5:
        return [{
            'Title': '请输入需要查询钻孔U单的产品型号。',
            'IcoPath': 'Images\\SYE.ico'
        }]

    url = 'http://eip.sye.com.cn:8181/bpm/r?wf_num=R_QA001_B042&wf_gridnum=V_QA001_G013&wf_action=edit&wf_docunid=c9fce6490fd3004f920a0e50f30fb3a34528&rdm=' + \
        str(random())+'&Status=全部&type=钻孔&isSearch=true&page=1&row=25&scxh='+param
    
    res = get_url(url)
    if res is None:
        return LOGIN_ERROR
    try:
        uds = res.json()
    except Exception as e:
        return QUERY_ERROR
    for ud in uds['rows']:
        try:
            if ud['WF_CurrentNodeName']=='已结束':
                result.append({
                    'Title': ud['Subject'],
                    'SubTitle': ud['WF_DocCreated'] + ' (已结束)',
                    'IcoPath': 'Images\\SYE.ico',
                    "ContextData": ud['WF_OrUnid'],
                    'JsonRPCAction': {
                        'method': 'open_url',
                        'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B062&wf_docunid='+ud['WF_OrUnid']]
                    }
                })
            elif ud['WF_CurrentNodeName']=='已归档':
                result.append({
                    'Title': ud['Subject'],
                    'SubTitle': ud['WF_DocCreated'] + ' (已归档)',
                    'IcoPath': 'Images\\SYE.ico',
                    "ContextData": ud['WF_OrUnid'],
                    'JsonRPCAction': {
                        'method': 'open_url',
                        'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B062&wf_docunid='+ud['WF_OrUnid']]
                    }
                })
            else:
                result.append({
                    'Title': ud['Subject'],
                    'SubTitle': ud['WF_DocCreated'],
                    'IcoPath': 'Images\\SYE.ico',
                    "ContextData": ud['WF_OrUnid'],
                    'JsonRPCAction': {
                        'method': 'open_url',
                        'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B036&wf_docunid='+ud['WF_OrUnid']]
                    }
                })  
        except Exception as e:
            return [{
                    'Title': '出现错误',
                    'IcoPath': 'Images\\SYE.ico'
                    }]
    if not result:
        result = QUERY_EMPTY.copy()
        result[0]['SubTitle'] = '未找到 {} 的钻孔工具U单。'.format(param)
        return result
    else:
        result.sort(key=lambda v: v['SubTitle'], reverse=True)
        return result

def query_xbbud(param):
    # 在生益ERP系统中根据料号名查询铣板边U单
    result = []
    param = param.strip()
    if len(param) < 5:
        return [{
            'Title': '请输入需要查询铣板边U单的产品型号。',
            'IcoPath': 'Images\\SYE.ico'
        }]

    url = 'http://eip.sye.com.cn:8181/bpm/r?wf_num=R_QA001_B006&wf_gridnum=V_QA001_G005&wf_action=edit&wf_docunid=c2ec269c06cbc049690a45f0d79e17838732&rdm=' + \
        str(random())+'&Status=ok&div=铣板边&page=1&rows=25&udxh='+param
    
    res = get_url(url)

    if res is None:
        return LOGIN_ERROR
    try:
        uds = res.json()
    except Exception as e:
        return QUERY_ERROR
    for ud in uds['rows']:
        try:
            if ud['WF_CurrentNodeName']=='已结束':
                result.append({
                    'Title': ud['Subject'],
                    'SubTitle': ud['WF_DocCreated'] + ' (已结束)',
                    'IcoPath': 'Images\\SYE.ico',
                    "ContextData": ud['WF_OrUnid'],
                    'JsonRPCAction': {
                        'method': 'open_url',
                        'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B062&wf_docunid='+ud['WF_OrUnid']]
                    }
                })
            elif ud['WF_CurrentNodeName']=='已归档':
                result.append({
                    'Title': ud['Subject'],
                    'SubTitle': ud['WF_DocCreated'] + ' (已归档)',
                    'IcoPath': 'Images\\SYE.ico',
                    "ContextData": ud['WF_OrUnid'],
                    'JsonRPCAction': {
                        'method': 'open_url',
                        'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B062&wf_docunid='+ud['WF_OrUnid']]
                    }
                })
            else:
                result.append({
                    'Title': ud['Subject'],
                    'SubTitle': ud['WF_DocCreated'],
                    'IcoPath': 'Images\\SYE.ico',
                    "ContextData": ud['WF_OrUnid'],
                    'JsonRPCAction': {
                        'method': 'open_url',
                        'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B036&wf_docunid='+ud['WF_OrUnid']]
                    }
                })  
        except Exception as e:
            return [{
                    'Title': '出现错误',
                    'IcoPath': 'Images\\SYE.ico'
                    }]
    if not result:
        result = QUERY_EMPTY.copy()
        result[0]['SubTitle'] = '未找到 {} 的钻孔工具U单。'.format(param)
        return result
    else:
        result.sort(key=lambda v: v['SubTitle'], reverse=True)
        return result

def query_gjud(param):
    # 在生益ERP系统中根据料号名查询工具U单
    result = []
    param = param.strip()
    if len(param) < 5:
        return [{
            'Title': '请输入需要查询工具U单的产品型号。',
            'IcoPath': 'Images\\SYE.ico'
        }]

    url = 'http://eip.sye.com.cn:8181/bpm/r?wf_num=R_QA001_B006&wf_gridnum=V_QA001_G005&wf_action=edit&wf_docunid=6bcf9c2b04771043510a0a40b56a22803f45&Status=ok&page=1&rows=25&rdm=' + \
        str(random())+'&udxh='+param
    res = get_url(url)
    if res is None:
        return LOGIN_ERROR
    try:
        uds = res.json()
    except Exception as e:
        return QUERY_ERROR
    for ud in uds['rows']:
        if 'leixing' in ud:
            leixing = ud['leixing']
        elif 'beizuangongju' in ud:
            leixing = ud['beizuangongju']
        try:
            if 'jielun' in ud:
                result.append({
                    'Title': (ud['udbh'] + ': ' + ud['udxh'].strip() + ' - 申请' + ud['WF_ProcessName']+': ' + ud['quexianmiaoshu']).replace('\r', ' ').replace('\n', ' '),
                    'SubTitle': ud['WF_DocCreated'] + ' : ' + ud['jielun'].replace('\r', ' ').replace('\n', ' '),
                    'IcoPath': 'Images\\SYE.ico',
                    "ContextData": ud['udbh'],
                    'JsonRPCAction': {
                        'method': 'open_url',
                        'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B062&wf_docunid='+ud['WF_OrUnid']]
                    }
                })
            else:
                result.append({
                    'Title': (ud['udbh'] + ': ' + ud['udxh'].strip() + ' - 申请' + ud['WF_ProcessName']+': ' + ud['quexianmiaoshu']).replace('\r', ' ').replace('\n', ' '),
                    'SubTitle': ud['WF_DocCreated'] + ' : 长边补偿值 ' + ud['cfxbcz1'] + '‰ , 短边补偿值 ' + ud['dfxbcz1'] + '‰',
                    'IcoPath': 'Images\\SYE.ico',
                    "ContextData": ud['udbh'],
                    'JsonRPCAction': {
                        'method': 'open_url',
                        'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B062&wf_docunid='+ud['WF_OrUnid']]
                    }
                })
        except Exception as e:
            return [{
                    'Title': '出现错误',
                    'IcoPath': 'Images\\SYE.ico'
                    }]
    if not result:
        result = QUERY_EMPTY.copy()
        result[0]['SubTitle'] = '未找到 {} 的工具U单。'.format(param)
        return result
    else:
        result.sort(key=lambda v: v['Title'], reverse=True)
        return result


def context_gjud(param):
    # 右键显示对应的工具U单内容
    result = []
    url = 'http://eip.sye.com.cn:8181/bpm/r?wf_num=R_QA001_B006&wf_gridnum=V_QA001_G005&wf_action=edit&wf_docunid=6bcf9c2b04771043510a0a40b56a22803f45&Status=ok&page=1&rows=25&rdm=' + \
        str(random())+'&udbh='+param
    res = get_url(url)
    if res is None:
        return LOGIN_ERROR
    try:
        uds = res.json()
    except Exception as e:
        return QUERY_ERROR
    for ud in uds['rows']:
        result.append({
            'Title': '产品型号：' + ud['udxh'],
            'IcoPath': 'Images\\SYE.ico',
            'JsonRPCAction': {
                'method': 'open_url',
                'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B062&wf_docunid='+ud['WF_OrUnid']]
            }
        })
        result.append({
            'Title': '工单编号：' + ud['gongdanhao3'],
            'IcoPath': 'Images\\Blank.png',
            'JsonRPCAction': {
                'method': 'open_url',
                'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B062&wf_docunid='+ud['WF_OrUnid']]
            }
        })
        result.append({
            'Title': '申请时间：' + ud['WF_DocCreated'],
            'IcoPath': 'Images\\Blank.png',
            'JsonRPCAction': {
                'method': 'open_url',
                'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B062&wf_docunid='+ud['WF_OrUnid']]
            }
        })
        result.append({
            'Title': '开单类别：' + ud['WF_ProcessName'],
            'IcoPath': 'Images\\Blank.png',
            'JsonRPCAction': {
                'method': 'open_url',
                'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B062&wf_docunid='+ud['WF_OrUnid']]
            }
        })
        result.append({
            'Title': 'U单状态：'+ud['WF_CurrentNodeName']+'　　耗时：'+ud['alltime'],
            'IcoPath': 'Images\\Blank.png',
            'JsonRPCAction': {
                'method': 'open_url',
                'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B062&wf_docunid='+ud['WF_OrUnid']]
            }
        })
        result.append({
            'Title': '缺陷数量：' + ud['buhegeshuliang'] + ud['danwei'] + ' (批量总数：' + ud['piliang'] + ud['danwei2'] + ')',
            'IcoPath': 'Images\\Blank.png',
            'JsonRPCAction': {
                'method': 'open_url',
                'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B062&wf_docunid='+ud['WF_OrUnid']]
            }
        })
        result.append({
            'Title': '缺陷描述：',
            'SubTitle': '　　'+ud['quexianmiaoshu'].replace('\r', ' ').replace('\n', ' '),
            'IcoPath': 'Images\\Blank.png',
            'JsonRPCAction': {
                'method': 'open_url',
                'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B062&wf_docunid='+ud['WF_OrUnid']]
            }
        })
        result.append({
            'Title': '处理结论：',
            'SubTitle': '　　'+ud['jielun'],
            'IcoPath': 'Images\\Blank.png',
            'JsonRPCAction': {
                'method': 'open_url',
                'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B062&wf_docunid='+ud['WF_OrUnid']]
            }
        })

    return result


def query_hmd(param):
    # 在生益ERP系统中查询型号上网黑名单
    result = []
    param = param.strip()
    if len(param) < 5:
        return [{
            'Title': '请输入需要查询黑名单的产品型号。',
            'IcoPath': 'Images\\SYE.ico'
        }]

    url = 'http://eip.sye.com.cn:8181/bpm/r?wf_num=D_CSP002_J004&wf_gridnum=V_CSP002_G004&page=1&rows=100&sort=WF_DocCreated&order=desc&rdm=' + \
        str(random())+'&searchStr='+param
    res = get_url(url)
    if res is None:
        return LOGIN_ERROR
    try:
        hmds = res.json()
    except Exception as e:
        return QUERY_ERROR
    for hmd in hmds['rows']:
        result.append({
            'Title': '['+hmd['WF_CurrentNodeName']+'] '+hmd['Subject'].strip() + ' 于 ' + hmd['WF_DocCreated']+' 申请特殊型号评审。',
            'SubTitle': '申请人：'+hmd['WF_AddName_CN'],
            'IcoPath': 'Images\\SYE.ico',
            "ContextData": hmd['WF_OrUnid'],
            'JsonRPCAction': {
                'method': 'open_url',
                'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B062&wf_docunid='+hmd['WF_OrUnid']]
            }
        })

    url = 'http://eip.sye.com.cn:8181/bpm/r?wf_num=D_CSP002_J010&wf_gridnum=V_CSP002_G010&page=1&rows=100&sort=WF_EndTime&order=desc&rdm=' + \
        str(random())+'&searchStr='+param
    res = get_url(url)
    if res is None:
        return LOGIN_ERROR
    try:
        hmds = res.json()
    except Exception as e:
        return QUERY_ERROR
    for hmd in hmds['rows']:
        result.append({
            'Title': '['+hmd['WF_CurrentNodeName']+'] '+hmd['Subject'].strip() + ' 申请于 ' + hmd['WF_DocCreated'],
            'SubTitle': '申请人：'+hmd['WF_AddName_CN'],
            'IcoPath': 'Images\\SYE.ico',
            "ContextData": hmd['WF_OrUnid'],
            'JsonRPCAction': {
                'method': 'open_url',
                'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B062&wf_docunid='+hmd['WF_OrUnid']]
            }
        })

    if not result:
        result = QUERY_EMPTY.copy()
        result[0]['Title'] = '未找到 {} 的黑名单信息，请检查关键词是否输入有误。'.format(param)
        return result
    else:
        return result


def context_hmd(param):
    # 右键显示对应的黑名单内容
    result = []
    url = 'http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B062&wf_docunid='+param
    res = get_url(url)
    if res is None:
        return LOGIN_ERROR
    try:
        from pyquery import PyQuery as pq
        doc = pq(res.content)
    except Exception as e:
        return QUERY_ERROR

    result.append({
        'Title': '产品型号：' + doc('#Subject').text(),
        'IcoPath': 'Images\\SYE.ico',
        'JsonRPCAction': {
            'method': 'open_url',
            'parameters': [url]
        }
    })
    result.append({
        'Title': '申请日期：' + doc('#WF_DocCreated').text(),
        'IcoPath': 'Images\\Blank.png',
        'JsonRPCAction': {
            'method': 'open_url',
            'parameters': [url]
        }
    })
    result.append({
        'Title': '申请人	：' + doc('#DeptName').text() + '　' + doc('#WF_AddName_CN').text() + '　📞 ' + doc('#Tel').text(),
        'IcoPath': 'Images\\Blank.png',
        'JsonRPCAction': {
            'method': 'open_url',
            'parameters': [url]
        }
    })
    result.append({
        'Title': '特殊型号内容：',
        'SubTitle': '　'+doc('#teshuxinghaoneirong').text().replace('\r', ' ').replace('\n', ' '),
        'IcoPath': 'Images\\Blank.png',
        'JsonRPCAction': {
            'method': 'open_url',
            'parameters': [url]
        }
    })
    if doc("input[name='pici']:checked"):
        result.append({
            'Title': '执行批次：' + doc("input[name='pici']:checked").val(),
            'IcoPath': 'Images\\Blank.png',
            'JsonRPCAction': {
                'method': 'open_url',
                'parameters': [url]
            }
        })
    result.append({
        'Title': '明确结论：' + doc("input[name='mqjl']:checked").val(),
        'IcoPath': 'Images\\Blank.png',
        'JsonRPCAction': {
            'method': 'open_url',
            'parameters': [url]
        }
    })

    return result


def query_pcd(param):
    # 在生益ERP系统中根据料号名查询偏差单
    result = []
    param = param.strip()
    if len(param) < 5:
        return [{
            'Title': '请输入需要查询偏差单的产品型号。',
            'IcoPath': 'Images\\SYE.ico'
        }]
    url = 'http://eip.sye.com.cn:8181/bpm/r?wf_num=R_QA002_B048&wf_gridnum=V_QA002_G042&search=true&rdm=' + \
        str(random())+'&chanpinxinghao='+param
    res = get_url(url)
    if res is None:
        return LOGIN_ERROR
    try:
        uds = res.json()
    except Exception as e:
        return QUERY_ERROR
    for ud in uds['rows']:
        result.append({
            'Title': ud['udanbianhao'] + ': ' + ud['chanpinxinghao'].strip() + ' 在 ' + ud['xuangongxu']+' 发现 ' + ud['quexianmingcheng'],
            'SubTitle': ud['WF_DocCreated'] + ' : ' + ud['quexianmiaoshu'].replace('\r', ' ').replace('\n', ' '),
            'IcoPath': 'Images\\SYE.ico',
            "ContextData": ud['udanbianhao'],
            'JsonRPCAction': {
                'method': 'open_url',
                'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B062&wf_docunid='+ud['WF_OrUnid']]
            }
        })
    if not result:
        result = QUERY_EMPTY.copy()
        result[0]['Title'] = '未找到 {} 的偏差单，请检查关键词是否输入有误。'.format(param)
        return result
    else:
        result.sort(key=lambda v: v['Title'], reverse=True)
        return result


def context_pcd(param):
    # 右键显示对应的偏差单内容
    result = []
    url = 'http://eip.sye.com.cn:8181/bpm/r?wf_num=R_QA002_B048&wf_gridnum=V_QA002_G042&div=DC&page=1&rows=100&search=true&rdm=' + \
        str(random())+'&udanbianhao='+param
    res = get_url(url)
    if res is None:
        return LOGIN_ERROR
    try:
        uds = res.json()
    except Exception as e:
        return QUERY_ERROR
    for ud in uds['rows']:
        result.append({
            'Title': '产品型号：' + ud['chanpinxinghao'],
            'IcoPath': 'Images\\SYE.ico',
            'JsonRPCAction': {
                'method': 'open_url',
                'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B062&wf_docunid='+ud['WF_OrUnid']]
            }
        })
        result.append({
            'Title': '工单编号：' + ud['gongdanhao3'],
            'IcoPath': 'Images\\Blank.png',
            'JsonRPCAction': {
                'method': 'open_url',
                'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B062&wf_docunid='+ud['WF_OrUnid']]
            }
        })
        result.append({
            'Title': '申请时间：' + ud['WF_DocCreated'],
            'IcoPath': 'Images\\Blank.png',
            'JsonRPCAction': {
                'method': 'open_url',
                'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B062&wf_docunid='+ud['WF_OrUnid']]
            }
        })
        result.append({
            'Title': '缺陷数量：' + ud['buhegeshuliang'] + ' (批量总数：' + ud['piliang'] + ')',
            'IcoPath': 'Images\\Blank.png',
            'JsonRPCAction': {
                'method': 'open_url',
                'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B062&wf_docunid='+ud['WF_OrUnid']]
            }
        })
        result.append({
            'Title': '缺陷描述：',
            'SubTitle': '　　'+ud['quexianmiaoshu'].replace('\r', ' ').replace('\n', ' '),
            'IcoPath': 'Images\\Blank.png',
            'JsonRPCAction': {
                'method': 'open_url',
                'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B062&wf_docunid='+ud['WF_OrUnid']]
            }
        })
        result.append({
            'Title': '初步分析：',
            'SubTitle': '　　'+ud['qchuliyijian'].replace('\r', ' ').replace('\n', ' '),
            'IcoPath': 'Images\\Blank.png',
            'JsonRPCAction': {
                'method': 'open_url',
                'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B062&wf_docunid='+ud['WF_OrUnid']]
            }
        })
        result.append({
            'Title': '原因分析：',
            'SubTitle': '　　'+ud['yuanyinfenxi'].replace('\r', ' ').replace('\n', ' '),
            'IcoPath': 'Images\\Blank.png',
            'JsonRPCAction': {
                'method': 'open_url',
                'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B062&wf_docunid='+ud['WF_OrUnid']]
            }
        })
        result.append({
            'Title': '改善措施：',
            'SubTitle': '　　'+ud['gaishancuoshi'].replace('\r', ' ').replace('\n', ' '),
            'IcoPath': 'Images\\Blank.png',
            'JsonRPCAction': {
                'method': 'open_url',
                'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B062&wf_docunid='+ud['WF_OrUnid']]
            }
        })
        result.append({
            'Title': '处理结论：',
            'SubTitle': '　　'+ud['lscheck'],
            'IcoPath': 'Images\\Blank.png',
            'JsonRPCAction': {
                'method': 'open_url',
                'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B062&wf_docunid='+ud['WF_OrUnid']]
            }
        })

    return result


def query_mkt(param):
    # 查询市场部新型号立项单
    result = []
    param = param.strip()
    if len(param) < 5:
        return [{
            'Title': '请输入需要查询市场部立项的产品型号。',
            'IcoPath': 'Images\\SYE.ico'
        }]
    url = 'http://eip.sye.com.cn:8181/bpm/r?wf_num=R_MKT008_B015&wf_gridnum=V_MKT008_G007&wf_action=edit&page=1&rows=25&wf_docunid=9ce6133705918047c508b2408ffa347323b7&isSearch=true&rdm=' + \
        str(random())+'&syxh='+param
    res = get_url(url)
    if res is None:
        return LOGIN_ERROR
    try:
        pns = res.json()
        if pns['total']==0:
            url = 'http://eip.sye.com.cn:8181/bpm/r?wf_num=R_MKT008_B015&wf_gridnum=V_MKT008_G007&wf_action=edit&page=1&rows=25&wf_docunid=9ce6133705918047c508b2408ffa347323b7&isSearch=true&rdm=' + \
                str(random())+'&Subject='+param
            res = get_url(url)
            pns = res.json()
    except Exception as e:
        return QUERY_ERROR
    for pn in pns['rows']:
        result.append({
            'Title': '[{0}] {1}'.format(pn['productscope'],pn['Subject']),
            'SubTitle': '{0}：{1} --> {2}'.format(pn['WF_DocCreated'],pn['WF_AddName_CN'],pn['receiver_show']),
            'IcoPath': 'Images\\SYE.ico',
            "ContextData": pn['WF_OrUnid'],
            'JsonRPCAction': {
                'method': 'open_url',
                'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B062&wf_docunid='+pn['WF_OrUnid']]
            }
        })
    if not result:
        result = QUERY_EMPTY.copy()
        result[0]['Title'] = '未找到 {} 的立项型号，请检查关键词是否输入有误。'.format(param)
        return result
    else:
        return result
    
def query_hk(param):
    # 在生益ERP系统中根据料号名查询黄卡
    result = []
    param = param.strip()
    if len(param) < 5:
        return [{
            'Title': '请输入需要查询黄卡的产品型号。',
            'IcoPath': 'Images\\SYE.ico'
        }]

    url = 'http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_PE002_B011&wf_gridnum=V_PE002_G023&wf_action=edit&page=1&rows=25&wf_docunid=f349b6430d92104c7b0aa3807b3985b113dd&Status=ok&rdm=' + \
        str(random())+'&ProductionModel='+param
    res = get_url(url)
    if res is None:
        return LOGIN_ERROR
    try:
        hks = res.json()
    except Exception as e:
        return QUERY_ERROR
    for hk in hks['rows']:
        result.append({
            'Title': hk['WF_DocCreated']+': '+hk['scxh']+' - ' + hk['erji'],
            'SubTitle': hk['xpswt'].replace('\r', ' ').replace('\n', ' '),
            'IcoPath': 'Images\\SYE.ico',
            "ContextData": hk['WF_OrUnid'],
            'JsonRPCAction': {
                'method': 'open_url',
                'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B062&wf_docunid='+hk['WF_OrUnid']]
            }
        })
    if not result:
        result = QUERY_EMPTY.copy()
        result[0]['Title'] = '未找到 {} 的黄卡，请检查关键词是否输入有误。'.format(param)
        return result
    else:
        return result


def query_ecn(param):
    # 在生益ERP系统中根据料号名查询工艺建议书（ECN）
    result = []
    param = param.strip()
    if len(param) < 5:
        return [{
            'Title': '请输入需要查询工艺建议书的产品型号。',
            'IcoPath': 'Images\\SYE.ico'
        }]

    url = 'http://eip.sye.com.cn:8181/bpm/r?wf_num=R_QA005_B009&wf_gridnum=V_QA005_G006&wf_action=edit&wf_docunid=cc8ca80408811040df095d80c66c5da18854&liuchengzhuangtai=0&Status=ok&page=1&rows=100&rdm=' + \
        str(random())+'&syxh='+param
    res = get_url(url)
    if res is None:
        return LOGIN_ERROR
    try:
        ecns = res.json()
    except Exception as e:
        return QUERY_ERROR
    for ecn in ecns['rows']:
        result.append({
            'Title': ecn['Subject'] + ' - ' + ecn['dayzt'],
            'SubTitle': '申请时间：'+ecn['WF_DocCreated']+' ~ '+ecn['WF_EndTime'],
            'IcoPath': 'Images\\SYE.ico',
            "ContextData": ecn['WF_OrUnid'],
            'JsonRPCAction': {
                'method': 'open_url',
                'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B062&wf_docunid='+ecn['WF_OrUnid']]
            }
        })
    if not result:
        result = QUERY_EMPTY.copy()
        result[0]['SubTitle'] = '未找到 {} 的工艺建议书。'.format(param)
        return result
    else:
        return result


def query_fgud(param):
    # 在生益ERP系统中根据料号名查询返工U单
    result = []
    param = param.strip()
    if len(param) < 5:
        return [{
            'Title': '请输入需要查询返工U单的产品型号。',
            'IcoPath': 'Images\\SYE.ico'
        }]

    url = 'http://eip.sye.com.cn:8181/bpm/r?wf_num=R_CSP010_B002&wf_gridnum=V_CSP010_G005&wf_action=edit&wf_docunid=5aa82421020850432008c980ec26f11ddc50&Status=ok&WF_Status=all&page=1&rows=200&rdm=' + \
        str(random())+'&chanpinxinghao='+param
    res = get_url(url)
    if res is None:
        return LOGIN_ERROR
    try:
        uds = res.json()
    except Exception as e:
        return QUERY_ERROR
    for ud in uds['rows']:
        result.append({
            'Title': ud['chanpinxinghao'] + ' 在 ' + ud['WF_DocCreated'] + ' 申请 ' + ud['ltype'],
            'SubTitle': ud['quexianmiaoshu'],
            'IcoPath': 'Images\\SYE.ico',
            "ContextData": ud['WF_OrUnid'],
            'JsonRPCAction': {
                'method': 'open_url',
                'parameters': ['http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_S003_B062&wf_docunid='+ud['WF_OrUnid']]
            }
        })
    if not result:
        result = QUERY_EMPTY.copy()
        result[0]['SubTitle'] = '未找到 {} 的返工U单。'.format(param)
        return result
    else:
        return result


def query_lld(param):
    # 在生益ERP系统中查询联络单待办消息
    result = []
    params = re.split(r'\s+', param.strip())
    # 获取我的待办中的联络单
    url = 'http://eip.sye.com.cn:8181/bpm/r?wf_num=R_Mail_B003&wf_gridnum=V_Mail_G007&wf_action=edit&wf_docunid=8a800c8a0db560417f0a5000290e5067eec5&page=1&rows=1000&sort=StratTime&order=desc&rdm=' + \
        str(random())
    res = get_url(url)
    if res is None:
        return LOGIN_ERROR
    try:
        msgs = res.json()
    except Exception as e:
        return QUERY_ERROR
    for msg in msgs['rows']:
        result.append({
            'Title': msg['StratTime'][:16]+' '+'[待办]'+msg['Subject'],
            'SubTitle': msg['DeptName']+' '+msg['Deptgroup']+' '+msg['WF_AddName_CN'],
            'IcoPath': 'Images\\SYE.ico',
            "ContextData": msg['StratTime'],
            'JsonRPCAction': {
                'method': 'open_url',
                'parameters': ['http://eip.sye.com.cn:8181/bpm/form?wf_num=F_Mail_Amailshow&wf_action=read&wf_docunid='+msg['DocUnid']]
            }
        })

    # 获取我的待阅中的联络单
    payload = {
        'rdm': str(random()),
        'page': '1',
        'rows': '500',
        'sort': 'StratTime',
        'order': 'desc'
    }
    try:
        msgs = get_url(
            'http://eip.sye.com.cn:8181/bpm/r?wf_num=R_Mail_B006&wf_gridnum=V_Mail_G002', params=payload).json()
    except Exception as e:
        return QUERY_ERROR
    for msg in msgs['rows']:
        result.append({
            'Title': msg['StratTime'][:16]+' '+'[待阅]'+msg['Subject'],
            'SubTitle': msg['DeptName']+' '+msg['Deptgroup']+' '+msg['WF_AddName_CN'],
            'IcoPath': 'Images\\SYE.ico',
            "ContextData": msg['StratTime'],
            'JsonRPCAction': {
                'method': 'open_url',
                'parameters': ['http://eip.sye.com.cn:8181/bpm/form?wf_num=F_Mail_Amailshow&wf_action=read&wf_docunid='+msg['DocUnid']]
            }
        })

    # 获取发件箱中联络单
    try:
        msgs = get_url(
            'http://eip.sye.com.cn:8181/bpm/r?wf_num=D_Mail_J003&wf_gridnum=V_Mail_G003', params=payload).json()
    except Exception as e:
        return QUERY_ERROR
    for msg in msgs['rows']:
        result.append({
            'Title': msg['StratTime'][:16]+' '+'[已发送]'+msg['Subject'],
            'SubTitle': msg['DeptName']+' '+msg['Deptgroup']+' '+msg['WF_AddName_CN'],
            'IcoPath': 'Images\\SYE.ico',
            "ContextData": msg['StratTime'],
            'JsonRPCAction': {
                'method': 'open_url',
                'parameters': ['http://eip.sye.com.cn:8181/bpm/form?wf_num=F_Mail_Amailshow&wf_action=read&wf_docunid='+msg['DocUnid']]
            }
        })

    for param in params:
        if param.startswith('-') and len(param) > 1:
            result = list(filter(lambda v: param[1:].lower() not in v['Title'].lower(
            ) and param[1:].lower() not in v['SubTitle'].lower(), result))
        else:
            result = list(filter(lambda v: param.lower() in v['Title'].lower(
            ) or param.lower() in v['SubTitle'].lower(), result))
    result.sort(key=lambda v: v['ContextData'], reverse=True)
    if not result:
        result = QUERY_EMPTY.copy()
        result[0]['SubTitle'] = '未找到关键词包含 {} 的联络单。'.format(param)
        return result
    else:
        return result


def query_iso(param):
    # 在生益ERP系统中查询ISO文件
    result = []
    param = param.strip()
    if len(param) < 2:
        return [{
            'Title': '请输入需要查询ISO文件的关键词。',
            'IcoPath': 'Images\\SYE.ico'
        }]
    param = re.split(r'\s+', param)
    filters = param[1:]
    param = param[0]
    url = 'http://eip.sye.com.cn:8181/bpm/rule?wf_num=R_SYS002_B002&wf_gridnum=V_SYS002_G001&Folder=001&Folder=001&page=1&rows=100&sort=WF_OrUnid&order=asc&rdm=' + \
        str(random())+'&m='+param
    res = get_url(url)
    if res is None:
        return LOGIN_ERROR
    try:
        data = res.json()
    except Exception as e:
        return QUERY_ERROR
    for row in data['rows']:
        result.append({
            'Title': row['FileNum'].strip()+row['Version']+' '+row['FileName'],
            'SubTitle': row['zhidingren']+' 于 '+row['WF_DocCreated']+' 发布。',
            'IcoPath': 'Images\\SYE.ico',
            "ContextData": row['WF_OrUnid'],
            'JsonRPCAction': {
                'method': 'open_ie_url',
                'parameters': ['http://eip.sye.com.cn/bpm/form?wf_num=F_SYS002_A009&wf_action=read&wf_docunid='+row['WF_OrUnid']]
            }
        })
    for key in filters:
        if key.startswith('-') and len(key) > 1:
            result = list(filter(lambda v: key[1:].lower() not in v['Title'].lower(
            ) and key[1:].lower() not in v['SubTitle'].lower(), result))
        else:
            result = list(filter(lambda v: key.lower() in v['Title'].lower(
            ) or key.lower() in v['SubTitle'].lower(), result))
    if not result:
        result = QUERY_EMPTY.copy()
        result[0]['SubTitle'] = '未找关键词包含 {} 的文件。'.format(param)
        return result
    else:
        return result


def query_ti(param):
    # 在生益ERP系统中查询上网受控通告文件
    result = []
    param = param.strip()
    if len(param) < 2:
        return [{
            'Title': '请输入需要查询TI通告文件的关键词。',
            'IcoPath': 'Images\\SYE.ico'
        }]
    param = re.split(r'\s+', param)
    filters = param[1:]
    param = param[0]

    url = 'http://eip.sye.com.cn:8181/bpm/r?wf_num=R_SYS002_B022&wf_gridnum=V_SYS002_G014&wf_action=edit&wf_docunid=ee7df6dd0a0a1048cb092340148c197bbcec&rdm=' + \
        str(random())+'&FileName='+param
    res = get_url(url)
    if res is None:
        return LOGIN_ERROR
    try:
        data = res.json()
    except Exception as e:
        return QUERY_ERROR
    for row in data['rows']:
        result.append({
            'Title': row['FileNum'].strip()+row['Version']+' '+row['FileName'],
            'SubTitle': row['zhidingren']+' 于 '+row['WF_DocCreated']+' 发布，失效日期：'+row['shixiaoriqi'],
            'IcoPath': 'Images\\SYE.ico',
            "ContextData": row['WF_OrUnid'],
            'JsonRPCAction': {
                'method': 'open_ie_url',
                'parameters': ['http://eip.sye.com.cn/bpm/rule?wf_num=R_S003_B062&wf_docunid='+row['WF_OrUnid']]
            }
        })
    for key in filters:
        if key.startswith('-') and len(key) > 1:
            result = list(filter(lambda v: key[1:].lower() not in v['Title'].lower(
            ) and key[1:].lower() not in v['SubTitle'].lower(), result))
        else:
            result = list(filter(lambda v: key.lower() in v['Title'].lower(
            ) or key.lower() in v['SubTitle'].lower(), result))
    if not result:
        result = QUERY_EMPTY.copy()
        result[0]['SubTitle'] = '未找关键词包含 {} 的文件。'.format(param)
        return result
    else:
        return result


def query_npi(param):
    # 同时查询黄卡、黑名单及偏差单
    param = param.strip()
    if len(param) < 5:
        return []

    result = []
    for v in query_hk(param):
        result.append(v.copy())
    for v in query_hmd(param):
        result.append(v.copy())
    for v in query_pcd(param):
        result.append(v.copy())
    return result


if __name__ == '__main__':
    print(query_xbbud('88660'))
