import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mlai-lab-secret-key'
    
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://Mlai:1234@localhost/mlai_lab'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    EXPERIMENT_TIMEOUT = 3600
    
    DB_HOST = 'localhost'
    DB_USER = 'Mlai'
    DB_PASSWORD = '1234'
    DB_NAME = 'mlai_lab'
    
    CONTAINER_LABEL = 'mlai-lab-vulnerability'
    PORT_MIN = 10000
    PORT_MAX = 13000
    
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
    
    DOCKER_CONFIGS = {
        'SQL注入-入门': {'use_docker_compose': True, 'port': 80},
        'SQL注入-中级': {'use_docker_compose': True, 'port': 80},
        'SQL注入-高级': {'use_docker_compose': True, 'port': 80},
        '反射型XSS': {'use_docker_compose': True, 'port': 80},
        '存储型XSS': {'use_docker_compose': True, 'port': 80},
        'DOM型XSS': {'use_docker_compose': True, 'port': 80},
        'PHP反序列化': {'use_docker_compose': True, 'port': 80},
        'Python反序列化': {'use_docker_compose': True, 'port': 8000},
        '文件上传': {'use_docker_compose': True, 'port': 80},
        'CSRF-Easy': {'use_docker_compose': True, 'port': 80},
        'CSRF-Hard': {'use_docker_compose': True, 'port': 80}
    }

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
