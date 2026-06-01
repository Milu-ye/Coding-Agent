import os
import pathlib

from anthropic import Anthropic
from configs import app_config
client = Anthropic(base_url=app_config.BASE_URL, api_key=app_config.API_KEY)
WORKDIR = pathlib.Path(os.getcwd())