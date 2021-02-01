"""
# KPI Gateway API
"""

import json
import logging
import os

from flask import jsonify

logger = logging.getLogger(__name__)


def authenticate(request):
    token = os.environ.get('AUTH_HEADER_TOKEN')
    auth_header_field = os.environ.get('AUTH_HEADER_FIELD', 'auth')
    if request.args.get(auth_header_field) == token:
        return True
    if request.headers.get(auth_header_field) == token:
        return True

    return False


def run_metrics_endpoint(request):
    data = {}
    try:
        if not authenticate(request):
            return jsonify({'error': 'NOT_AUTHENTICATED'}), 401

        if request.method != 'POST':
            return jsonify({'error': 'METHOD_NOT_ALLOWED'}), 405

        data = request.get_json()
        if data.get('metrics') is None:
            return jsonify({'error': {'metrics': 'field not set'}}), 400
        
        for metric in data.get('metrics', []):
            print('metric-fire {}'.format(json.dumps(metric)))

        return jsonify({}), 204
    except Exception as e:
        logging.error('exception {} for metrics {}'.format(str(e), json.dumps(data)))
        return jsonify({
            'status': 'error',
            'msg': str(e)
        }), 400
