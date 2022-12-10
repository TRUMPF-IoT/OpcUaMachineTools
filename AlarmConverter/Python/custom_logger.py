# MIT License

# Copyright (c) 2022 TRUMPF Werkzeugmaschinen SE + Co. KG

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import logging
import logging.handlers
import os

# Add custom log level TRACE between Info and Warning. Warnings in libraries are logged, but not Infos.
TRACE_LOG_LEVEL = 25 #  log levels https://docs.python.org/3.5/howto/logging.html#logging-levels
logging.addLevelName(TRACE_LOG_LEVEL, "TRACE")
def trace(self, message, *args, **kws):
    if self.isEnabledFor(TRACE_LOG_LEVEL):
        # Yes, logger takes its '*args' as 'args'.
        self._log(TRACE_LOG_LEVEL, message, args, **kws) 
logging.Logger.trace = trace


def setup_logging(basePath, fileName):   
    os.makedirs(basePath, exist_ok=True)
    loggingFullPath = os.path.join(basePath, fileName)    
    rootLogger = logging.getLogger()
    rootLogger.setLevel(TRACE_LOG_LEVEL)
    logFormatter = logging.Formatter("%(asctime)s [%(name)-30.30s]  %(message)s")
    fileHandler = logging.handlers.RotatingFileHandler(loggingFullPath, maxBytes=1000000, backupCount=7, encoding='utf-8')
    fileHandler.setFormatter(logFormatter)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)
    rootLogger.addHandler(consoleHandler)


def set_level(log_level):
    if log_level == "standard":
        logging.getLogger().setLevel(TRACE_LOG_LEVEL)
    elif log_level == "verbose":
        logging.getLogger().setLevel(logging.INFO)

