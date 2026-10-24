"""Compare numeric model reports at prespecified absolute1e-7; identities exact."""
import csv
import json
import math
from pathlib import Path
import sys


def compare(a,b,path='',tolerance=1e-7):
    if isinstance(a,bool) or isinstance(b,bool):
        if a!=b:raise AssertionError(path)
    elif isinstance(a,(int,float)) and isinstance(b,(int,float)):
        if not math.isfinite(a) or not math.isfinite(b) or abs(a-b)>tolerance:raise AssertionError(f'{path}: {a} != {b}')
    elif isinstance(a,dict) and isinstance(b,dict):
        if a.keys()!=b.keys():raise AssertionError(path+' keys')
        for k in a:compare(a[k],b[k],path+'/'+str(k),tolerance)
    elif isinstance(a,list) and isinstance(b,list):
        if len(a)!=len(b):raise AssertionError(path+' length')
        for i,(x,y) in enumerate(zip(a,b)):compare(x,y,path+'/'+str(i),tolerance)
    elif a!=b:raise AssertionError(path)


def directory(left,right):
    names=['results.json','predictions.csv','configurations.csv','analysis.md','model-stability.svg','chronological-errors.svg','inputs-manifest.json']
    def cell(value):
        try:return float(value)
        except ValueError:return value
    for name in names:
        a=(Path(left)/name).read_text(encoding='utf-8');b=(Path(right)/name).read_text(encoding='utf-8')
        if name.endswith('.json'):compare(json.loads(a),json.loads(b),name)
        elif name.endswith('.csv'):
            compare([[cell(v) for v in r] for r in csv.reader(a.splitlines())],
                    [[cell(v) for v in r] for r in csv.reader(b.splitlines())],name)
        elif a!=b:raise AssertionError(name+' text differs')


if __name__=='__main__':directory(*sys.argv[1:3])
