# config.py

import os


class ConfigSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigSingleton, cls).__new__(cls)
            cls._instance._init_config()
        return cls._instance

    def _init_config(self):
        # Load environment variables or settings
        self.MOVIE_API_URL = os.getenv('MOVIE_API_URL', 'https://demo.credy.in/api/v1/maya/movies/')
        self.MOVIE_API_USERNAME = os.getenv('MOVIE_API_USERNAME', 'iNd3jDMYRKsN1pjQPMRz2nrq7N99q4Tsp9EY9cM0')
        self.MOVIE_API_PASSWORD = os.getenv('MOVIE_API_PASSWORD', 'Ne5DoTQt7p8qrgkPdtenTK8zd6MorcCR5vXZIJNfJwvfafZfcOs4reyasVYddTyXCz9hcL5FGGIVxw3q02ibnBLhblivqQTp4BIC93LZHj4OppuHQUzwugcYu7TIC5H1')


# Usage:
config = ConfigSingleton()

