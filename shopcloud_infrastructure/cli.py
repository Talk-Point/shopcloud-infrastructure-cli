import requests
import os, time
from shopcloud_secrethub import SecretHub


class Gauge:
    def __init__(self, name: str, **kwargs):
        self.name = name
        self.value = kwargs.get('value')
        self.labels = kwargs.get('labels', [])

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'value': self.value,
            'labels': self.labels,
        }


class MetricRegistry:
    """
    registry = MetricRegistry()
    registry.gauge('job_up', value=0, labels=[{'name': 'my-job', 'instance': 'airflow-production'}])
    registry.gauge('job_last_success_unixtime', labels=[{'name': 'test'}])
    registry.gauge('api_http_requests_total', value=12, labels=[{'operation': 'create'}])
    registry.gauge('process_cpu_seconds_total', value=1)
    registry.gauge('http_request_duration_seconds', value=1)
    registry.push()
    """

    def __init__(self):
        self.metrics = []
        self.hub = SecretHub(
            user_app='kpi-signal', 
            api_token=os.environ.get('SECRETHUB_TOKEN')
        )

    def gauge(self, name: str, **kwargs):
        self.metrics.append(
            Gauge(
                name, 
                value=kwargs.get('value'), 
                labels=kwargs.get('labels'),
            )
        )

    def _push(self, metrics: list):
        response = requests.post(
            'https://europe-west3-shopcloud-analytics.cloudfunctions.net/metric-gateway-api',
            headers={
                'User-Agent': 'shopcloud-infrastructure',
                'auth': self.hub.read('talk-point/kpi-gateway/auth-token')
            },
            json={
                'metrics': metrics
            }
        )
        return response

    def push(self):
        metrics = [x.to_dict() for x in self.metrics]
        
        is_success = False
        for i in range(10): # 
            response = self._push(metrics)
            print('metric-gateway-api status_code: {} content: {}'.format(response.status_code, response.content))
        
            if (200 <= response.status_code <= 299):
                is_success = True
                break

            time.sleep(2)
        
        if not is_success:
            raise Exception('Can not push metrics')


#registry = MetricRegistry()
#registry.gauge('job_up', value=1, labels=[{'name': 'shopcloud-infrastructure-cli', 'instance': 'tests'}])

#registry.gauge('job_up', value=0, labels=[{'name': 'my-job', 'instance': 'airflow-production'}])
#registry.gauge('job_last_success_unixtime', labels=[{'name': 'test'}])
#registry.gauge('api_http_requests_total', value=12, labels=[{'operation': 'create'}])
#registry.gauge('process_cpu_seconds_total', value=1)
#registry.gauge('http_request_duration_seconds', value=1)
#registry.push()