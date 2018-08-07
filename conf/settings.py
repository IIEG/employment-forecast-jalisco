import os
from os.path import join, dirname
from dotenv import load_dotenv

# LOAD ENV VARIABLES
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# READ FOLDER NAMES
DATA_FOLDER = os.environ.get("DATA_FOLDER")
CONF_FOLDER = os.environ.get("CONF_FOLDER")
DATASETS    = os.environ.get("DATASETS")
OUTPUT      = os.environ.get("OUTPUT")
MODEL       = os.environ.get("MODEL")
LOGS        = os.environ.get("LOGS")

# READ FILE NAMES
DATA_FILE        = os.environ.get("DATA_FILE")
VALIDATION_FILE  = os.environ.get("VALIDATION_FILE")
RUNTIME          = os.environ.get("RUNTIME")
TRAIN_RESULTS    = os.environ.get("TRAIN_RESULTS")
PRODUCTION_MODEL = os.environ.get("PRODUCTION_MODEL")

# READ DATABASE VARIABLES
CONNECTION_STRING   = os.environ.get("CONNECTION_STRING")
QUERY_STRING        = os.environ.get("QUERY_STRING")

# READ ML LABELS
TRAIN_LABEL     = os.environ.get("TRAIN_LABEL")
TEST_LABEL      = os.environ.get("TEST_LABEL")
VALIDATE_LABEL  = os.environ.get("VALIDATE_LABEL")
TRAIN_SPLIT     = os.environ.get("TRAIN_SPLIT")
TEST_SPLIT      = os.environ.get("TEST_SPLIT")
VALIDATE_SPLIT  = os.environ.get("VALIDATE_SPLIT")
MAX_LAGS        = os.environ.get("MAX_LAGS")
MIN_LAGS        = os.environ.get("MIN_LAGS")
ALPHA           = os.environ.get("ALPHA")
RAND_SEARCH     = os.environ.get("RAND_SEARCH")

# DETERMINE PROJECT DIR AND ABSOLUTE PATHS
PROJECT_DIR     = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
DATA_PATH       = join(PROJECT_DIR, DATA_FOLDER)
DATASETS_PATH   = join(DATA_PATH, DATASETS)
CONF_PATH       = join(PROJECT_DIR, CONF_FOLDER)
MODEL_PATH      = join(PROJECT_DIR, MODEL)


class FilesConf:

    class Paths:
        data        = DATA_PATH
        conf        = CONF_PATH
        datasets    = DATASETS_PATH
        model       = MODEL_PATH
        output      = join(DATA_PATH, OUTPUT)
        logs        = join(PROJECT_DIR, LOGS)

    class FileNames:
        data        = join(DATA_PATH, DATASETS, DATA_FILE)
        validation  = join(DATA_PATH, DATASETS, VALIDATION_FILE)
        runtime     = join(CONF_PATH, RUNTIME)
        train_results    = join(MODEL_PATH, TRAIN_RESULTS)
        production_model = join(MODEL_PATH, PRODUCTION_MODEL)

class DatabaseConf:
    connection_string = CONNECTION_STRING
    query_string      = QUERY_STRING


class ModelConf:

    random_search = int(RAND_SEARCH)

    class labels:
        train       = TRAIN_LABEL
        test        = TEST_LABEL
        validate    = VALIDATE_LABEL

    class splits:
        train       = float(TRAIN_SPLIT)
        test        = float(TEST_SPLIT)
        validate    = float(VALIDATE_SPLIT)

    class lags:
        max_lags    = int(MAX_LAGS)
        min_lags    = int(MIN_LAGS)
        alpha       = float(ALPHA)