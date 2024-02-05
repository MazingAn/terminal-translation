#!/bin/python3
import requests
import hashlib
from termcolor import colored
import re
import sys

import sqlite3
import os


class Trans:
    APPPID = "20240201001957074"
    APIKEY = "q3cdGcjWzp5JcPv30Yu_"
    APIURL = "http://api.fanyi.baidu.com/api/trans/vip/translate"
    SALT = "1234567258"

    ERRORCODE = {
        52000: "正常",
        52001: "请求超时",
        52002: "系统错误",
        52003: "未授权用户",
        54000: "内部错误",
        54001: "签名错误 ",
    }

    def __init__(self):
        pass

    def dotrans(self, query_value):
        """do translate, 从网络上获取翻译信息
        参数：query_value  要查询的词
        返回：网页获取内容"""

        if query_value is None or query_value == "":
            print(colored("请输入您要查询的内容", "red"))
            return None
        params = self.makeparams(query_value)
        try:
            response = requests.get(self.APIURL, params=params)
            return response.json()
        except Exception:
            print(colored("网络异常", "red"))
            return None

    def checkstatus(self, code):
        """如果有错误，输出错误信息"""
        if code != 52000:
            print(colored(self.ERRORCODE[code], "red"))

    def makeparams(self, query_value):
        """返回url参数"""
        params = {
            "from": "auto",
            "to": "auto",
            "appid": self.APPPID,
            "salt": self.SALT,
            "sign": self.makesign(query_value),
            "q": query_value,
        }
        return params

    def makesign(self, query_value):
        str = self.APPPID + query_value + self.SALT + self.APIKEY
        md5 = hashlib.md5()
        md5.update(str.encode("utf-8"))
        return md5.hexdigest()

    def ischinese(self, query_value):
        if re.match(r"[a-z]|[A-Z]", query_value) is None:
            return True
        else:
            return False

    def output(self, query_value):
        data = self.dotrans(query_value)
        if data is not None:
            if "error_code" in data.keys():
                self.checkstatus(data["error_code"])
                print(colored("\tNone(没有合适的解释)", "red"))
            else:
                print(colored("翻译结果：", "green"))
                for value in data["trans_result"]:
                    print(colored("\t%s", "yellow") % value["src"])
                    print(colored("\t%s", "green") % value["dst"])
                self.save_to_db(query_value, data)
        else:
            print("没有找到释义")

    def save_to_db(self, query_value, data):
        dbpath = os.path.join(os.path.expanduser("~"), ".trans.db")
        conn = sqlite3.connect(dbpath)
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS words(word VARCHAR(32), trans VARCHAR(128), count INTEGER)"
        )

        rs = cur.execute(
            'SELECT * FROM words WHERE word="' + query_value + '"'
        ).fetchall()
        if len(rs) > 0:
            count = cur.execute(
                'SELECT count FROM words WHERE word="' + query_value + '"'
            ).fetchall()[0][0]
            newcount = int(count) + 1
            cur.execute(
                "UPDATE words SET count="
                + str(newcount)
                + ' WHERE word="'
                + query_value
                + '"'
            )
        else:
            tr = data["trans_result"][0]
            cur.execute(
                'INSERT INTO words VALUES("' + query_value + '","' + tr["dst"] + '", 1)'
            )
        cur.close()
        conn.commit()
        conn.close()


q = None
if len(sys.argv) > 1:
    if sys.argv[1].startswith("-"):
        if sys.argv[1] == "-l":
            dbpath = os.path.join(os.path.expanduser("~"), ".trans.db")
            conn = sqlite3.connect(dbpath)
            cur = conn.cursor()
            cur.execute("SELECT * FROM words ORDER BY count DESC")

            for eachword in cur.fetchall():
                colorname = "yellow"
                rate = "低频"
                if int(eachword[2]) > 4:
                    rate = "高频"
                    colorname = "red"
                if int(eachword[2]) < 5 and int(eachword[2]) > 2:
                    rate = "中频"
                    colorname = "green"
                print(
                    colored(
                        "%s====>%s                %s次查询            (%s)", colorname
                    )
                    % (eachword[0], eachword[1], eachword[2], rate)
                )
            cur.close()
            conn.commit()
            conn.close()
        if sys.argv[1] == "-h":
            print("you can use -l to list words you searched.")
            print("you can use -h to show this help message.")
            print("you can use trans word to trans")
    else:
        q = sys.argv[1]
        t = Trans()
        t.output(q)
else:
    print(colored("请输入一个参数", "red"))
