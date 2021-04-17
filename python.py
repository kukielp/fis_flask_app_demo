from flask import Flask, render_template, request
from load_data import *
from util import *
from get_methods import *
from post_methods import *

app = Flask(__name__)


@app.route('/select_data')
def select():
    return json.dumps(get_vendors())


@app.route('/select_data_500')
def select_500():
    return json.dumps(get_vendors_500())



@app.route('/get_500')
def get_500():
    return get_500_response()


@app.route('/render', methods=["GET"])
def render_sample():
    return render_template('render.html')


@app.route('/')
def hello_world():
    return 'Hello world from Flask!'


@app.route('/add_item', methods=['POST', 'GET'])
def add_tem():
    if request.method == 'POST':
        content = request.get_json(silent=True)
        vendor_id = insert_vendor(content['vendor_name'])
        return json.dumps(vendor_id)
    else:
        return 'Use POST'


@app.route('/load_data')
def load():
    create_tables()
    insert_vendor('AKM Semiconductor Inc.')
    insert_vendor('Asahi Glass Co Ltd.')
    insert_vendor('Daikin Industries Ltd.')
    insert_vendor('Dynacast International Inc.')
    return 'Data is loaded'


if __name__ == '__main__':
    app.run()


 # env LDFLAGS='-L/usr/local/lib -L/usr/local/opt/openssl/lib -L/usr/local/opt/readline/lib' pip install -r requirements.txt 