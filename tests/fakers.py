import tempfile
import os
import shutil
import subprocess
import random
import ConfigParser


def gen_test_conf():
    """Generates a ConfigParser object built with test options values"""
    global_config_options = {
            "pidfile": tempfile.mkstemp(suffix=".pid", dir='/tmp')[1],
            "databases_storage_path": tempfile.mkdtemp(dir='/tmp'),  # Will be randomly set later
            "database_store": tempfile.mkstemp(suffix=".json", dir="/tmp")[1],
            "port": str(random.randint(4142, 60000)),
            "activity_log": tempfile.mkstemp(suffix=".log", dir="/tmp")[1],
            "errors_log": tempfile.mkstemp(suffix="_errors.log", dir="/tmp")[1],
            "max_cache_size": 1024,
    }
    config = ConfigParser.RawConfigParser()
    config.add_section('global')

    for key, value in global_config_options.iteritems():
        config.set('global', key, value)

    return config


class TestDaemon(object):
    def __init__(self):
        self.bootstrap_conf()
        self.process = None

        self.port = self.config.get('global', 'port')

    def __del__(self):
        for key, value in self.config.items('global'):
            if not isinstance(value, int) and os.path.exists(value):
                if os.path.isfile(value):
                    os.remove(value)
                elif os.path.isdir(value):
                    shutil.rmtree(value)

        os.remove(self.conf_file_path)

    def bootstrap_conf(self):
        self.conf_file_path = tempfile.mkstemp(suffix=".conf", dir="/tmp")[1]
        self.config = gen_test_conf()

        with open(self.conf_file_path, 'w') as f:
            self.config.write(f)

    def start(self):
        self.process = subprocess.Popen(['elevator',
                                         '--config', self.conf_file_path,
                                         '--port', self.port])

    def stop(self):
        self.process.kill()
