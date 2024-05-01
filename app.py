from flask import Flask, render_template, request
import os
import re
import json
import requests
import datetime

app = Flask(__name__)

@app.route("/", methods=["GET"])
def hello_world():
    try:
        background_color = os.environ["APP_COLOR"]
    except:
        background_color = "#aaaaaa"
    return render_template("index.html", background_color=background_color)

@app.route("/update", methods=["POST"])
def update():
    new_color = request.form['color']
    regex = r"^#[0-z]{3,6}$"
    if not re.match(regex, new_color):
        abort(400)
    with open('/run/secrets/kubernetes.io/serviceaccount/namespace', 'rt') as f:
        namespace = f.read()
    with open('/run/secrets/kubernetes.io/serviceaccount/token', 'rt') as f:
        token = f.read()
    patch_data = {"data": {"APP_COLOR": new_color}}
    headers = {
        "Authorization": "Bearer {}".format(token),
        "Content-Type": "application/strategic-merge-patch+json",
        "Accept": "application/json"}
    reply_patch = requests.patch(
        "https://{host}:{port}/api/v1/namespaces/{namespace}/configmaps/configmap-test".format(
            host=os.environ["KUBERNETES_SERVICE_HOST"],
            port=os.environ["KUBERNETES_SERVICE_PORT_HTTPS"],
            namespace=namespace),
        headers=headers,
        data=json.dumps(patch_data),
        verify="/run/secrets/kubernetes.io/serviceaccount/ca.crt")
    rollout_data = {"spec": {"template": {"metadata": {"annotations": {"kubectl.kubernetes.io/restartedAt": datetime.datetime.now().isoformat() }}}}}
    reply_rollout = requests.patch(
        "https://{host}:{port}/apis/apps/v1/namespaces/{namespace}/deployments/configmap-test".format(
            host=os.environ["KUBERNETES_SERVICE_HOST"],
            port=os.environ["KUBERNETES_SERVICE_PORT_HTTPS"],
            namespace=namespace),
        data=json.dumps(rollout_data),
        headers=headers,
        verify="/run/secrets/kubernetes.io/serviceaccount/ca.crt")
    return "Updating value to {}. Patch status code is {}. Rolout status code is {}.".format(new_color, reply_patch.status_code, reply_rollout.status_code)
