import json
import re
import time
from json.decoder import JSONDecodeError

from auto_sign.config import generateConfig
from auto_sign.utility.function import now, nowstamp, sendQmsgInfo, send_telegram
from datetime import datetime

txt = now()+"\n\n────── PT签到 ──────\n\n"


def signin(session, url, name):
    # 完整签到url
    global txt
    # hdarea签到
    if url == "https://www.hdarea.co":
        attendance_url = url + '/sign_in.php'
        data = {"action": "sign_in"}
        with session.post(attendance_url, data) as res:
            r = re.compile(r'获得了\d+魔力值')
            r1 = re.compile(r'重复')
            print(res.text)
            if r.search(res.text):
                tip = ' 签到成功'
            elif r1.search(res.text):
                tip = ' 重复签到'
            else:
                tip = 'cookie已过期'
            print(now(), ' 网站：%s' % url, tip)
            txt += '网站：<a href="%s">%s</a>' % (url, name) + tip + '\n'
    # 猫站签到
    elif url == "https://pterclub.com":
        attendance_url = url + '/attendance-ajax.php'
        with session.get(attendance_url) as res:
            try:
                msg = json.loads(res.text.encode('utf-8').decode('unicode-escape')).get('message')
            except JSONDecodeError:
                msg = res.text
            if '连续签到' in msg:
                tip = ' 签到成功'
            elif '重复刷新' in msg:
                tip = ' 重复签到'
            else:
                tip = ' cookie已过期'
            print(now(), ' 网站：%s' % url, tip)
            txt += '网站：<a href="%s">%s</a>' % (url, name) + tip + '\n'
    # 海胆签到
    elif url == "https://www.haidan.video":
        attendance_url = url + '/signin.php'
        with session.get(attendance_url) as res:
            r = re.compile(r'已经打卡')
            r1 = re.compile(r'退出')
            if r.search(res.text):
                tip = ' 签到成功'
            elif r1.search(res.text):
                tip = ' 重复签到'
            else:
                tip = ' cookie已过期!'
            print(now(), ' 网站：%s' % url, tip)
            txt += '网站：<a href="%s">%s</a>' % (url, name) + tip + '\n'
    # bschool
    elif url == "https://pt.btschool.club":
        attendance_url = url + '/index.php?action=addbonus'
        with session.get(attendance_url) as res:
            r = re.compile(r'今天签到您获得\d+点魔力值')
            r1 = re.compile(r'退出')
            if r.search(res.text):
                tip = ' 签到成功'
            elif r1.search(res.text):
                tip = ' 重复签到'
            else:
                tip = ' cookie已过期'
            print(now(), ' 网站：%s' % url, tip)
            txt += '网站：<a href="%s">%s</a>' % (url, name) + tip + '\n'
    # lemonhd
    elif url == "https://lemonhd.org":
        attendance_url = url + '/attendance.php'
        with session.get(attendance_url) as res:
            r = re.compile(r'已签到')
            r1 = re.compile(r'请勿重复刷新')
            # print(res.text)
            if r.search(res.text) and r1.search(res.text) is None:
                tip = ' 签到成功'
            elif r1.search(res.text):
                tip = ' 重复签到'
            else:
                tip = ' cookie已过期'
            print(now(), ' 网站：%s' % url, tip)
            txt += '网站：<a href="%s">%s</a>' % (url, name) + tip + '\n'
    # hares白兔
    elif url == "https://club.hares.top":
        attendance_url = url + '/attendance.php?action=sign'
        headers = {'Accept': 'application/json'}
        session.headers.update(headers)
        # print(session.headers)
        with session.get(attendance_url) as res:
            try:
                msg = json.loads(res.text.encode('utf-8').decode('unicode-escape')).get('msg')
            except JSONDecodeError:
                msg = res.text
            r = re.compile(r'签到成功')
            r1 = re.compile(r'已经签到')
            print(msg)
            if r.search(msg) and r1.search(msg) is None:
                tip = ' 签到成功'
            elif r1.search(msg):
                tip = ' 重复签到'
            else:
                tip = ' cookie已过期'
            print(now(), ' 网站：%s' % url, tip)
            txt += '网站：<a href="%s">%s</a>' % (url, name) + tip + '\n'
    elif url == "https://www.pttime.org":
        attendance_url = url + '/attendance.php?type=sign'

        with session.get(attendance_url) as res:
            # print(now(), 'Request URL[%s] status code: [%d]' % (attendance_url, res.status_code))
            r = re.compile(r'请勿重复刷新')
            r1 = re.compile(r'今日签到成功')
            if r.search(res.text):
                tip = get_bonus_info_pttime_repeat(res)
                tip += '[请勿重复签到]'
            elif r1.search(res.text):
                # tip = ' 签到成功!'
                tip = get_bonus_info_pttime(res)
            else:
                if res.status_code != 200:
                    print(now(), 'Request URL[%s] status code: [%d]' % (attendance_url, res.status_code))
                    tip = f'\n\n站点访问异常，错误码：[{res.status_code}]\n\n'
                else:
                    tip = '\n\ncookie已过期\n\n'
                print(now(), res.text + '\n')

            print(now(), ' 网站：%s' % url, tip)
            txt += '<a href="%s">%s</a>站点: \n' % (url, name) + tip + '\n'
    else:
        attendance_url = url + '/attendance.php'
        # 绕过cf5秒盾
        # session = cloudscraper.create_scraper(session)

        # 解决PT站点第一次请求/attendance.php页面签到时，抓取到的魔力值为签到前的旧数据问题
        with session.get(attendance_url, timeout=15) as res:
            print(now(), 'Request URL[%s] status code: [%d]' % (attendance_url, res.status_code))

        # 等待0.5秒再请求
        time.sleep(0.5)

        with session.get(attendance_url, timeout=15) as res:
            # print(now(), 'Request URL[%s] status code: [%d]' % (attendance_url, res.status_code))
            r = re.compile(r'请勿重复刷新')
            r1 = re.compile(r'[签簽]到已得[\s]*\d+')
            # r2 = re.compile(r'簽到已得[\s]*\d+')
            # if url == "https://www.hddolby.com" or url == "https://pt.btschool.club":
            # print(res.text)
            if r.search(res.text):
                tip = get_bonus_info(res)
                tip += '[请勿重复签到]'
            elif r1.search(res.text):
                # tip = ' 签到成功!'
                tip = get_bonus_info(res)
            else:
                if res.status_code != 200:
                    print(now(), 'Request URL[%s] status code: [%d]' % (attendance_url, res.status_code))
                    tip = f'\n\n站点访问异常，错误码：[{res.status_code}]\n\n'
                else:
                    tip = '\n\ncookie已过期\n\n'
                print(now(), res.text + '\n')


            print(now(), ' 网站：%s' % url, tip)
            txt += '<a href="%s">%s</a>站点: \n' % (url, name) + tip + '\n'
    txt += '────────────────\n\n'

def smart_to_number(s: str):
    """
    将字符串转换为数字（自动识别整数/小数/科学计数法）。
    支持包含货币符号、逗号、中文单位等。
    """
    if not isinstance(s, str):
        return None

    # 1. 去除空格
    s = s.strip()

    # 2. 删除常见货币符号和单位
    s = re.sub(r'[￥¥$€元円円,，]', '', s)

    # 3. 匹配数字（含小数点、科学计数法）
    match = re.match(r'^[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?$', s)
    if not match:
        return None  # 不是有效数字

    # 4. 转换为 float，再判断是否为整数
    num = float(s)
    return int(num) if num.is_integer() else num

def get_bonus_info_pttime(res):
    res_str = "\n"
    this_time_bonus = -1
    r_html_tag = re.compile(r'<[^>]+>', re.S)
    # 第X次签到
    r_times = re.compile(r'第[\s\S]*?次签到')
    if r_times.search(res.text):
        res_times = r_times.findall(res.text)[0]
        res_times = r_html_tag.sub('', res_times)
        res_str += f'{res_times}成功！\n\n'

    # 已连续签到天数
    r_continuous_days = re.compile(r'已连续签到[\s\S]*?天')
    if r_continuous_days.search(res.text):
        res_days = r_continuous_days.findall(res.text)[0]
        res_days = r_html_tag.sub('', res_days)
        res_str += f'{res_days}\n\n'

    # 获得魔力值
    r_bonus = re.compile(r'本次签到获得[\s\S]*?个魔力值')
    if r_bonus.search(res.text):
        res_bonus = r_bonus.findall(res.text)[0]
        res_bonus = r_html_tag.sub('', res_bonus)
        res_str += f'{res_bonus}\n\n'
        res_bonus = res_bonus[6:-4]
        print(f'nun_bonus: {res_bonus}')
        this_time_bonus = smart_to_number(res_bonus)

    # 当前魔力值
    r_bonus = re.compile(r'\]: [\d,\.]+\[')
    if r_bonus.search(res.text):
        res_bonus = r_bonus.findall(res.text)[0]
        res_bonus = res_bonus[2:-1]
        print(f'nun_bonus: {res_bonus}, this_time_bonus: {this_time_bonus}')
        num_bonus = smart_to_number(res_bonus)
        num_bonus += this_time_bonus
        res_str += f'当前魔力值:{num_bonus:,}\n\n'

    return res_str

def get_bonus_info_pttime_repeat(res):
    res_str = "\n"
    # r_html_tag = re.compile(r'<[^>]+>', re.S)
    # 获取总签到天数，第xx次签到成功！
    r_totally_days = re.compile(r'总签到：\d+天')
    if r_totally_days.search(res.text):
        res_days = r_totally_days.findall(res.text)[0]
        res_days = res_days[4:-1]
        res_str += f'第 {res_days} 次签到成功！\n\n'

    # 已连续签到天数
    r_continuous_days = re.compile(r'本次连续签到开始时间：\d+')
    if r_continuous_days.search(res.text):
        res_days = r_continuous_days.findall(res.text)[0]
        res_days = res_days[11:]
        date_first = datetime.strptime(res_days, '%Y%m%d')
        date_second = datetime.now()
        delta_days = abs((date_second - date_first).days)+1
        res_str += f'已连续签到 {delta_days} 天\n\n'

    # 获得魔力值
    r_bonus = re.compile(r'获得魔力值：[\s\S]*</b>')
    if r_bonus.search(res.text):
        res_bonus = r_bonus.findall(res.text)[0]
        r_bonus = re.compile(r'\d+', re.S)
        if r_bonus.search(res_bonus):
            res_bonus = r_bonus.findall(res_bonus)[0]
            res_str += f'本次签到获得 {res_bonus} 个魔力值\n\n'
        else:
            res_str += '本次签到未获得魔力值\n\n'

    # 当前魔力值
    r_bonus = re.compile(r'\]: [\d,\.]+\[')
    if r_bonus.search(res.text):
        res_bonus = r_bonus.findall(res.text)[0]
        # 去除html标签
        # result_bonus = r_html_tag.sub('', res_bonus)
        # 匹配数字、英文逗号、英文句号
        # r_bonus_num = re.compile(r'[\d,\.]+')
        # result_bonus = r_bonus_num.findall(result_bonus)[0]
        res_bonus = res_bonus[2:-1]
        res_str += f'当前魔力值:{res_bonus}\n\n'

    return res_str

def get_bonus_info(res):
    res_str = "\n"
    r_success = re.compile(r'[签簽]到成功')
    if r_success.search(res.text):
        # 获取签到天数，连续签到天数，获得魔力值等
        r_res = re.compile(r'[签簽]到成功[\s\S]*</span>')
        if r_res.search(res.text):
            r_matches = r_res.findall(res.text)
            contents = r_matches[0]
            # print(now(), 'contents: %s', contents)
            r_html_tag = re.compile(r'<[^>]+>', re.S)
            result = r_html_tag.sub('', contents)
            # print(now(), 'result: %s' % result)
            # 截取天数信息
            r_days = re.compile(r'第[^。]*。')
            if r_days.search(result):
                result_days = r_days.findall(result)
                result_day_tmp = result_days[0]
                # 第xxx次签到成功
                r_day = re.compile(r'第[^，]*次[签簽]到')
                if r_day.search(result_day_tmp):
                    result_day = r_day.findall(result_day_tmp)[0]
                    res_str += result_day + "成功！\n\n"
                # 连续签到xxx天
                r_day = re.compile(r'已[连連][续續][签簽]到[\s\S]*天')
                if r_day.search(result_day_tmp):
                    result_day_cont = r_day.findall(result_day_tmp)[0]
                    res_str += result_day_cont + "\n\n"
                # 获得xxx个魔力值
                r_added_bonus = re.compile(r'本次[\s\S]*[个個]')
                if r_added_bonus.search(result_day_tmp):
                    result_bonus = r_added_bonus.findall(result_day_tmp)[0]
                    res_str += result_bonus + "魔力值\n\n"

            # 截取排名信息
            r_rank = re.compile(r'[签簽]到排名[\s\S]*')
            if r_rank.search(result):
                result_rank = r_rank.findall(result)
                result_rank_str = result_rank[0]
                find_idx = result_rank_str.index('/')
                result_rank_str = result_rank_str[0: find_idx - 1]
                res_str += result_rank_str + "\n\n"

            # print(now(), 'res_str: %s' % res_str)

            # 获取当前魔力值
            r_bonus = re.compile(r'\]:[\s\S]*\[[签簽]到')
            if r_bonus.search(res.text):
                result_bonus = r_bonus.findall(res.text)[0]
                # 去除html标签
                result_bonus = r_html_tag.sub('', result_bonus)
                # 匹配数字、英文逗号、英文句号
                r_bonus_num = re.compile(r'[\d,\.]+')
                result_bonus = r_bonus_num.findall(result_bonus)[0]
                # print("result_bonus: %s" % result_bonus)
                res_str += "当前魔力值: %s" % result_bonus + "\n\n"

    return res_str



# discuz系列签到
def signin_discuz_dsu(session, url, name):
    attendance_url = url + "/plugin.php?id=dsu_paulsign:sign&operation=qiandao&infloat=1&sign_as=1&inajax=1"
    hash_url = url + "/plugin.php?id=dsu_paulsign:sign"
    with session.get(hash_url) as hashurl:
        h = re.compile(r'name="formhash" value="(.*?)"')
        formhash = h.search(hashurl.text).group(1)
    data = {"qdmode": 3, "qdxq": "kx", "fastreply": 0, "formhash": formhash, "todaysay": ""}
    with session.post(attendance_url, data) as res:
        r = re.compile(r'签到成功')
        r1 = re.compile(r'已经签到')
        global txt
        if r.search(res.text):
            txt += '网站：<a href="%s">%s</a>' % (url, name) + " 签到成功 \n"
            print(now(), ' 网站：%s' % url, " 签到成功")
        elif r1.search(res.text):
            txt += '网站：<a href="%s">%s</a>' % (url, name) + " 重复签到 \n"
            print(now(), ' 网站：%s' % url, " 重复签到")
        else:
            txt += '网站：<a href="%s">%s</a>' % (url, name) + " cookie已过期 \n"
            print(now(), ' 网站：%s' % url, res.text)


# 不移之火签到
def signin_discuz_ksu(session, url, name):
    attendance_url = url + "/plugin.php?id=k_misign:sign&operation=qiandao"
    hash_url = url + "/plugin.php?id=k_misign:sign"
    with session.get(hash_url) as hashurl:
        h = re.compile(r'name="formhash" value="(.*?)"')
        # print(hashurl.text)
        formhash = h.search(hashurl.text).group(1)
    data = {"formhash": formhash, "format": "empty"}
    with session.post(attendance_url, data) as res:
        # print(res.text)
        r = re.compile(r'CDATA\[\]')
        r1 = re.compile(r'今日已签')
        global txt
        if r.search(res.text):
            txt += '网站：<a href="%s">%s</a>' % (url, name) + " 签到成功 \n"
            print(now(), ' 网站：%s' % url, " 签到成功")
        elif r1.search(res.text):
            txt += '网站：<a href="%s">%s</a>' % (url, name) + " 重复签到 \n"
            print(now(), ' 网站：%s' % url, " 重复签到")
        else:
            txt += '网站：<a href="%s">%s</a>' % (url, name) + " cookie已过期 \n"
            print(now(), ' 网站：%s' % url, res.text)


# hifi签到
def signin_hifi(session, url, name):
    attendance_url = url + "/sg_sign.htm"
    with session.post(attendance_url) as res:
        r = re.compile(r'成功')
        r1 = re.compile(r'今天已经')
        global txt
        if r.search(res.text):
            txt += '网站：<a href="%s">%s</a>' % (url, name) + " 签到成功 \n"
            print(now(), ' 网站：%s' % url, " 签到成功")
        elif r1.search(res.text):
            txt += '网站：<a href="%s">%s</a>' % (url, name) + " 重复签到 \n"
            print(now(), ' 网站：%s' % url, " 重复签到")
        else:
            txt += '网站：<a href="%s">%s</a>' % (url, name) + " cookie已过期 \n"
            print(now(), ' 网站：%s' % url, res.text)


def main():
    global txt
    print(now(), '--PT站开始签到--')
    [signin(config['session'], config['url'], config['name']) for config in generateConfig() if 'sign_in' in config['tasks']]
    print(now(), '--其他站开始签到--')
    [signin_discuz_dsu(config['session'], config['url'], config['name']) for config in generateConfig() if 'sign_in_discuz' in config['tasks']]
    [signin_hifi(config['session'], config['url'], config['name']) for config in generateConfig() if 'sign_in_hifi' in config['tasks']]
    [signin_discuz_ksu(config['session'], config['url'], config['name']) for config in generateConfig() if 'sign_in_discuz_ksu' in config['tasks']]
    # cookie过期发送qq推送信息
    r = re.compile(r'过期')
    r1 = re.compile(r'重复')
    # if r.search(txt) or r1.search(txt):
    #     # sendQmsgInfo(txt)
    #     send_telegram(txt)

    send_telegram(txt)



if __name__ == '__main__':
    main()
