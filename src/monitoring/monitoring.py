from prometheus_client import start_http_server, Counter
import time
import random

# Sample metrics
REQUEST_TIME = Gauge('request_processing_time', 'Time spent processing request')

@app.route('/data')
def data():
    start_time = time.time()
    # Logic to get and return data
    REQUEST_TIME.set(time.time() - start_time)
    return data

if __name__ == '__main__':
    start_http_server(8000)

REQUEST_COUNT = Counter('request_count', 'Total Request Count') 

def start_monitoring():
    start_http_server(8000)
    # metrics set up