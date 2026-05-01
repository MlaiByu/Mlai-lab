import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mlai-lab-secret-key'
    
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://Mlai:1234@localhost/mlai_lab'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    EXPERIMENT_TIMEOUT = 3600

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}