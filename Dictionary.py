#-*-coding:utf-8-*-
import os
import subprocess
rootdir = os.path.abspath(os.path.dirname(__file__))
dicpath = os.path.join(rootdir, "ipcdic_wine.dic")

if not os.path.exists(dicpath):
    print("creating dictionary...")
    cmd = "mecab-dict-index -f utf-8 -t utf-8 -d \"C:\Program Files\MeCab\dic\ipadic\" -u ipcdic_wine.dic wine.csv"
    subprocess.run(cmd)

def get_dic_path():
    return (dicpath)
