# -*- coding: utf-8 -*-
import platform
import xml.etree.ElementTree as ET
from os import path

from flask import request, flash, render_template, url_for, abort, current_app
import config
import base64
from datetime import datetime, timedelta
import json
from bs4 import BeautifulSoup
from functools import wraps
from sqlalchemy.ext.declarative import DeclarativeMeta


def access_required(resource_name):
    from admin.models import Resource
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not Resource.is_accessible(resource_name):
                abort(403)
            return fn(*args, **kwargs)

        return wrapper

    return decorator


class AlchemyEncoder(json.JSONEncoder):
    _visited_objs = []

    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # don't re-visit self
            if obj in self._visited_objs:
                return None
            self._visited_objs.append(obj)

            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    if isinstance(data, datetime):
                        data = data.strftime('%Y-%m-%d %H:%M:%S')
                    # this will fail on non-encodable values, like other classes
                    json.dumps(data)
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            return fields

        return json.JSONEncoder.default(self, obj)


def to_dict(data):
    jsonstr = json.dumps(data, cls=AlchemyEncoder,
                         check_circular=False, skipkeys=True)
    ret = json.loads(jsonstr)
    return ret

def init_app(app):
    def static_url(fn):
        filepath = path.join(app.static_folder, fn)
        if platform.system() == 'Windows':
            filepath = filepath.replace('/', '\\')
        v = path.getmtime(filepath)
        return url_for('static', filename=fn, v=int(v))

    @app.context_processor
    def ctx_pr():
        return {
            'static_url': static_url,
            # 'title': config.TITLE
        }


def args_get(key, default=None, type=None, required=False):
    val = request.args.get(key, default)
    if not val:
        if required:
            raise Exception('Missing query argument %r' % key)
        return default
    if type is not None:
        val = type(val)
    return val


def form_get(key, default=None, type=None, required=False):
    val = request.form.get(key, default)
    if not val:
        if required:
            raise Exception('Missing form argument %r' % key)
        return default
    if type is not None:
        val = type(val)
    return val


def flash_alert(level, msg):
    flash(render_template('alert.html', level=level, msg=msg))


def get_subelements(ele, tagname, only_one=True):
    ret = []
    for sub in ele:
        if tagname == sub.tag:
            if only_one:
                return sub
            ret.append(sub)
    return ret


def parse_output(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()
    statistics = get_subelements(root, 'statistics')
    total = get_subelements(statistics, 'total')
    all_tests_stat = get_subelements(total, 'stat', only_one=False)[-1]
    return all_tests_stat.attrib

def parse_redfish_output(filepath):
    with open(filepath) as inf:
        html = BeautifulSoup(inf.read(), 'html.parser')
        targetinput = html.find(attrs={"name": "parsed-results"})
        if targetinput is None:
            return
        value = targetinput.get('value')
        return json.loads(value)

def parse_uefi_validation_index(filepath):
    ret = {}
    with open(filepath) as inf:
        html = BeautifulSoup(inf.read())
        el_a = html.find_all(attrs={'class': 'list-group-item'})
        for a in el_a:
            a_id = a.get('id')
            if a_id and a_id.startswith('index'):
                if a.text.endswith('failed'):
		    ret['fail'] = ret.get('fail', 0) + 1
                elif a.text.endswith('successful'):
		    ret['success'] = ret.get('success', 0) + 1
        return ret

def excludes(keys=(), values=()):
    def _decorator(f):
        def _func(params):
            _the_params = {
                k: v for (k, v) in params.items()
                if (k not in keys) and (v not in values)}
            return f(_the_params)

        return _func

    return _decorator

def groupby2(iterObj, key):
    _dict = {}
    for i in iterObj:
        k = key(i)
        _dict.setdefault(k, [])
        _dict[k].append(i)
    return _dict.iteritems()

class StringCooker(object):
    @staticmethod
    def _translate(s, encoded):
        from string import maketrans   # 引用 maketrans 函数。
        intab = "AbdGhjm1pt9Z="
        outtab = "192AGZbdhjmpt"
        if encoded:
            trantab = maketrans(intab, outtab)
        else:
            trantab = maketrans(outtab, intab)
        return s.translate(trantab);
    
    def encode(self, s):
        encoded = base64.b64encode(s)
        return self._translate(encoded, True)
        
    def decode(self, s):
        encoded = self._translate(s, False)
        return base64.b64decode(encoded)

string_cooker = StringCooker()

def date_from_to(start, end, input_fmt='%Y-%m-%d', output_fmt='%Y-%m-%d'):
    '''
    start: '2017-08-25'
    end : '2017-08-31'
    ret: ['2017-08-25', '2017-08-26',...,'2017-08-31']
    '''
    startDate = datetime.strptime(start, input_fmt)
    endDate = datetime.strptime(end, input_fmt)
    n = 1
    ret = [startDate]
    while ret[-1] < endDate:
        ret.append(startDate + timedelta(days=n))
        n += 1
    ret = [r.strftime(output_fmt) for r in ret]
    return ret

def get_median(data):
    data.sort()
    half = len(data) // 2
    return (data[half] + data[~half]) / 2

def get_average(data):
    return sum(data) // len(data)

def get_variance(data):
    avg = get_average(data)
    n = len(data)
    return sum((x - avg) ** 2 for x in data) // n

def print_json(data):
    print json.dumps(data, indent=True)

def fill_null_flat(data):
    to_fill = None
    for idx, val in enumerate(data):
        if val is None:
            if to_fill is not None:
                data[idx] = to_fill
        else:
            to_fill = val
    return data

def fill_null_linear(data):
    # [0, null, null ,null , 8 ...] => [0, 2, 4, 6, 8, ...]
    def get_arr(a, b, lng):
        step = float(b - a) / (lng - 1)
        ret = [a]
        while len(ret) < lng - 1:
            ret.append(ret[-1] + step)
        ret += [b]
        return [round(i, 1) for i in ret]
    ret = []
    remains = data
    a = None
    b = None
    curpos = 0
    startpos = None
    while len(remains) > curpos:
        b = remains[curpos]
        if b is not None:
            if a is not None:
                if len(remains) - curpos == 1:
                    ret += get_arr(a, b, (curpos - startpos + 1))
                else:
                    ret += get_arr(a, b, (curpos - startpos + 1))[:-1]
                remains = remains[curpos - 1:]
                curpos = 0
                a = None
            else:
                startpos = curpos
                a = b
        curpos += 1
    return ret

def token_required(access_token):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            with current_app.app_context():
                token = args_get("token", required=True)
                if token != current_app.config[access_token]:
                    abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator


class ModelMixin(object):
    def to_dict(self):
        tablename = self.__tablename__
        table = self.metadata.tables[tablename]
        ret = {}
        for key in table.columns.keys():
            ret[key] = getattr(self, key)
        return ret

    @classmethod
    def get_model_columns(cls):
        model_inst = cls()
        tablename = model_inst.__tablename__
        table = model_inst.metadata.tables[tablename]
        return table.columns.keys()

def main():
    sample = [0.0, None, None, None, None, None, None, 6.0, None, None, None, None, None, None, 12.0, None, None, None, None, None, None, 17.0, None, None, None, None, None, None, 28.6, None, None, None, None, None, None, 40.2, None, None, None, None, None, None, 40.2, None, None, None, None, None, None, 40.2, None, None, None, None, None, None, 51.8, None, None, None, None, None, None, 63.4, None, None, None, None, None, None, 75.0, None, None, None, None, None, None, 82.9, None, None, None, None, None, None, 91.2, None, None, None, None, None, None, 99.7, None, None, None, None, None, None, 100.0]
    print len(sample)
    ret= fill_null_linear(sample)
    # ret = fill_null_flat(sample)
    print len(ret)
    print ret
    # print parse_output('./outputs/project 1/1/log-20170313-111655.html')
    # cooker = StringCooker()
    # s = 'thinkcloud'
    # assert cooker.decode(cooker.encode(s)) == s
    # print  date_from_to('2017-08-25', '2017-08-31', '%Y-%m-%d', '%Y/%m/%d')
    #print parse_redfish_output(r'C:\Users\wangwh8\workspace\redfish-ci\logs\ConformanceHtmlLog_11_14_2017_171247.html')
    # print parse_uefi_validation_index('/srv/project/standalone-page/outputs/uefi_validation/20/lnvgy_fw_uefi_iver15f-1.02_anyos_32-64/index.html')
if __name__ == '__main__':
    main()
