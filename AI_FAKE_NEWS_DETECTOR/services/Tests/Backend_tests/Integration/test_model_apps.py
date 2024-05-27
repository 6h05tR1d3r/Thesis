import pytest
import json
from unittest.mock import patch, mock_open

# Importing Flask app instances directly
from prediciton_services_LR.app import app as LRApp
from prediction_services_NB.app import app as NBApp
from prediction_services_PA.app import app as PAApp

# Test configurations for each app, adapted to directly use imported apps
app_configs = {
    "LRApp": {
        "client_app": LRApp,
        "base_url": "/predict_LR",
        "home_page_url": "/LR_page",
        "result_key": "LR",
        "together_url": "/LR/get_result",
        "together_key": "NB",
        "wc_url": "/getWCData",
        "tf_url": "/getTFData",
        "wc_data_keys": ["Fake", "Real"],
        "tf_data_keys": ["Fake", "Real"]
    },
    "NBApp": {
        "client_app": NBApp,
        "base_url": "/predict_NB",
        "home_page_url": "/NB_page",
        "result_key": "NB",
        "together_url": "/NB/get_result",
        "together_key": "LR",
        "wc_url": "/getWCData",
        "tf_url": "/getNBData",
        "wc_data_keys": ["Fake", "Real"],
        "tf_data_keys": ["Fake", "Real"]
    },
    "PAApp": {
        "client_app": PAApp,
        "base_url": "/predict_PA",
        "home_page_url": "/PA_page",
        "result_key": "PA",
        "together_url": "/PA/get_result",
        "together_key": "LR",
        "wc_url": "/getPAData",
        "tf_url": "/getWCData",
        "wc_data_keys": ["Fake", "Real"],
        "tf_data_keys": ["Fake", "Real"]
    }
}

@pytest.fixture(scope="module", params=["LRApp", "NBApp", "PAApp"])
def client(request):
    app = app_configs[request.param]['client_app']
    app.config['TESTING'] = True
    app.config['DEBUG'] = True
    client = app.test_client()
    return client, app_configs[request.param]

def test_home_page(client):
    client_instance, config = client
    response = client_instance.get(config['home_page_url'])
    assert response.status_code == 200

def test_predict_valid_data(client):
    client_instance, config = client
    response = client_instance.post(config['base_url'], data={'message': 'Some news article content'})
    assert response.status_code == 200
    result = json.loads(response.data)
    assert config['result_key'] in result['result']

def test_predict_together_valid_data(client):
    client_instance, config = client
    data = {'message': 'Some news article content'}
    response = client_instance.post(config['together_url'], data=data)
    assert response.status_code == 200
    result = json.loads(response.data)
    assert 'result' in result
    assert config['together_key'] in result['result']['result1']['result']

def test_predict_empty_data(client):
    client_instance, config = client
    response = client_instance.post(config['base_url'], data={'message': ''})
    assert response.status_code == 415
    result = json.loads(response.data)
    assert 'error' in result


def test_predict_wrong_method(client):
    client_instance, config = client
    response = client_instance.get(config['base_url'])
    assert response.status_code == 405
    result = json.loads(response.data)
    assert 'error' in result

def test_predict_together_empty_data(client):
    client_instance, config = client
    data = {'message': ''}
    response = client_instance.post(config['together_url'], data=data)
    assert response.status_code == 415
    result = json.loads(response.data)
    assert 'error' in result

def test_predict_together_numerical_data(client):
    client_instance, config = client
    data = {'message': 12121212}
    response = client_instance.post(config['together_url'], data=data)
    assert response.status_code == 415
    result = json.loads(response.data)
    assert 'error' in result

def test_handle_error_404(client):
    client_instance, config = client
    response = client_instance.get('/aaaaa')
    assert response.status_code == 404

def test_get_graph_data(client):
    client_instance, config = client
    response = client_instance.get(config['tf_url'])
    assert response.status_code == 200
    data = json.loads(response.data)
    assert set(config['tf_data_keys']).issubset(data.keys())

def test_get_wc_data(client):
    client_instance, config = client
    response = client_instance.get(config["wc_url"])
    assert response.status_code == 200
    data = json.loads(response.data)
    assert set(config['wc_data_keys']).issubset(data.keys())
