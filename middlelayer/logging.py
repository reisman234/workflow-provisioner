import sys
import logging

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stdout_handle = logging.StreamHandler(sys.stdout)
stdout_handle.setFormatter(formatter)
stderr_handle = logging.StreamHandler(sys.stderr)
stderr_handle.setFormatter(formatter)


logger = logging.getLogger("provisioner")
logger.setLevel(level=logging.DEBUG)
logger.addHandler(stdout_handle)
