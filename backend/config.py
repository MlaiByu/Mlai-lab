import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mlai-lab-secret-key'
    SERVER_PORT = int(os.environ.get('SERVER_PORT') or 8000)

    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_USER = os.environ.get('DB_USER') or 'mlai'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or 'Aa123456'
    DB_NAME = os.environ.get('DB_NAME') or 'mlai_lab'

    EXPERIMENT_TIMEOUT = 3600

    CONTAINER_LABEL = 'mlai-lab-vulnerability'
    PORT_MIN = 10000
    PORT_MAX = 13000
    MAX_CONTAINERS_PER_USER = 1

    DOCKER_VULN_MAP = {
        'SQL注入-入门': 'sqli-easy',
        'SQL注入-中级': 'sqli-medium',
        'SQL注入-高级': 'sqli-hard',
        '反射型XSS': 'xss-reflected',
        '存储型XSS': 'xss-stored',
        'DOM型XSS': 'xss-dom',
        'PHP反序列化': 'php-deserialization',
        'Python反序列化': 'python-deserialization',
        '文件上传': 'file-upload',
        'CSRF-Easy': 'csrf-easy',
        'CSRF-Hard': 'csrf-hard'
    }

    DOCKER_CONFIGS = {name: {'use_docker_compose': True, 'port': 80} for name in DOCKER_VULN_MAP}