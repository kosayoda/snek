import asyncio
import logging
import os
import pathlib
import sys
from logging import handlers

import arrow
import coloredlogs

start_time = arrow.utcnow()


def get_loc(path: os.PathLike) -> int:
    amount = 0

    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith('.py'):
                with open(os.path.join(root, file)) as f:
                    amount += len(f.readlines())

    return amount


LOC = get_loc('snek')

logging.TRACE = 5
logging.addLevelName(logging.TRACE, 'TRACE')


def trace_logger(self: logging.Logger, msg: str, *args, **kwargs) -> None:
    """Log messages with the `TRACE` level."""
    if self.isEnabledFor(logging.TRACE):
        self._log(logging.TRACE, msg, args, **kwargs)


logging.Logger.trace = trace_logger

LOG_LEVEL = getattr(logging, os.environ.get('SNEK_LOG_LEVEL', ''), logging.DEBUG)
LOG_FORMAT = '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
log_formatter = logging.Formatter(LOG_FORMAT)

log_file = pathlib.Path('logs', 'snek.log')
log_file.parent.mkdir(exist_ok=True)

file_handler = handlers.RotatingFileHandler(
    log_file,
    maxBytes=8388608,
    backupCount=7,
    encoding='utf-8'
)
file_handler.setFormatter(log_formatter)

root_logger = logging.getLogger()
root_logger.setLevel(LOG_LEVEL)
root_logger.addHandler(file_handler)

coloredlogs.DEFAULT_LEVEL_STYLES = {
    **coloredlogs.DEFAULT_LEVEL_STYLES,
    'trace': {'color': 246},
    'critical': {'background': 'red'},
    'debug': coloredlogs.DEFAULT_LEVEL_STYLES['info']
}
coloredlogs.DEFAULT_LOG_FORMAT = LOG_FORMAT

coloredlogs.install(logger=root_logger, stream=sys.stdout, level=logging.TRACE)

# Important warnings
logging.getLogger('asyncio').setLevel(logging.WARNING)
logging.getLogger('chardet').setLevel(logging.WARNING)
logging.getLogger('discord').setLevel(logging.WARNING)
logging.getLogger('websockets').setLevel(logging.WARNING)

log = logging.getLogger(__name__)
log.setLevel(LOG_LEVEL)

if os.name == 'nt':
    log.info('Setting WindowsSelectorEventLoopPolicy as Snek is running on Windows')
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
