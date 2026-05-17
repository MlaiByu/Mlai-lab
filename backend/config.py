import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mlai-lab-secret-key'
    SERVER_PORT = int(os.environ.get('SERVER_PORT') or 8000)

    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_USER = os.environ.get('DB_USER') or 'mlai'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or '1234'
    DB_NAME = os.environ.get('DB_NAME') or 'mlai_lab'

    EXPERIMENT_TIMEOUT = 3600

    CONTAINER_LABEL = 'mlai-lab-vulnerability'
    PORT_MIN = 10000
    PORT_MAX = 13000
    MAX_CONTAINERS_PER_USER = 1

    DOCKER_VULN_MAP = {
        'SQL Injection Easy': 'sqli-easy',
        'SQL Injection Medium': 'sqli-medium',
        'SQL Injection Hard': 'sqli-hard',
        'XSS Reflected': 'xss-reflected',
        'XSS Stored': 'xss-stored',
        'XSS DOM': 'xss-dom',
        'PHP Deserialization': 'php-deserialization',
        'Python Deserialization': 'python-deserialization',
        'File Upload': 'file-upload',
        'CSRF Easy': 'csrf-easy',
        'CSRF Hard': 'csrf-hard'
    }

    DOCKER_CONFIGS = {name: {'use_docker_compose': True, 'port': 80} for name in DOCKER_VULN_MAP}