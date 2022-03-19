"""..."""
import yaml
import os
from pathlib import Path
# if __name__ == '__main__':
#     sys.path.append(os.path.abspath(os.path.join(Path(__file__).parent.parent, os.path.pardir)))
# sys.path.append(os.path.abspath(os.path.join(Path(__file__).parent.parent, os.path.pardir)))
#-#from applib.tools_lib import pcformat
from .log import logger
info, debug, error, warn = logger.info, logger.debug, logger.error, logger.warning

_cache_conf = {}


def getConf(conf_path='./config.yaml', root_key=None, force_reload=False):
    global _cache_conf
    conf_file_path = os.path.abspath(conf_path)
    conf = _cache_conf.get(conf_file_path, None)

    if conf is None or force_reload:
        if force_reload:
            debug('force load conf from file %s', conf_file_path)
        assert os.path.exists(conf_file_path)
        with open(conf_file_path, 'rt', encoding='utf8') as yml:
            conf = yaml.load(yml, Loader=yaml.FullLoader) # https://github.com/yaml/pyyaml/wiki/PyYAML-yaml.load(input)-Deprecation

        _cache_conf[conf_file_path] = conf
#-#        debug('load done %s. %s key(s)', conf_file_path, len(conf))
#-#    else:
#-#        debug('get conf from cache %s', conf_file_path)

    if root_key:
        if root_key not in conf:
            error('conf no root_key %s in %s !!!', root_key, conf_file_path)
        conf = conf.get(root_key)

    return conf


if __name__ == '__main__':
    from applib.tools import pcformat
    conf = getConf('./config.yaml')
    info(pcformat(conf))
