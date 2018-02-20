from flask.views import MethodView
from flask import Blueprint, render_template, jsonify, request
from core import run_cmd_by_port, PORTS

from resource import iterShadowsocksResources


app = Blueprint("freess", __name__)

@app.route("/")
def index():
    return render_template("freess.html")

@app.route("/api/server")
def api_server():
    server_gen = iterShadowsocksResources()
    server_list = list(server_gen)
    ret = {
        "server_list": [s['result'] for s in server_list],
        "ports": PORTS,
        "url": server_list[0]['url'] if server_list else 'n/a'

    }
    return jsonify(ret)

@app.route("/api/localserver/run")
def localserver_run():
    port = request.args.get('port')
    cmd = request.args.get('cmd')
    if 0 == run_cmd_by_port(cmd, port):
        ret = "ok"
    else:
        ret = "fail"
    return ret
