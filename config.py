import os


class Config:
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")


class DevelopmentConfig(Config):
    pass


class StagingConfig(Config):
    pass


class ProductionConfig(Config):
    DEBUG = False


def load_config():
    """
    Load config for current application environment eg. dev, staging, prod
    """
    stage = os.environ.get("STAGE")
    config_to_stage_map = {
        "dev": DevelopmentConfig,
        "staging": StagingConfig,
        "prod": ProductionConfig
    }
    try:
        return config_to_stage_map[stage]
    except KeyError:
        print("Unable to load configs. An invalid STAGE was set."
              " Choose one from 'dev, staging, prod'")
    except Exception:
        print("Something went wrong while loading the configs")
