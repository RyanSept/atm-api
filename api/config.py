import os
import logging

logger = logging.getLogger(__name__)


class Config:
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    JWT_TOKEN_EXPIRY = int(os.environ.get("JWT_TOKEN_EXPIRY"))
    BUNDLE_ERRORS = True
    LOG_LEVEL = logging.DEBUG


class DevelopmentConfig(Config):
    pass


class StagingConfig(Config):
    pass


class ProductionConfig(Config):
    pass


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
        logger.debug("Unable to load configs. An invalid STAGE was set."
                     " Choose one from 'dev, staging, prod'")
    except Exception as error:
        logger.debug("Something went wrong while loading the configs.")
        logger.error(error)
