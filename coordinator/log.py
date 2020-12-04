import logging
class Log:
    def __init__(self,filename,level="INFO"):
        self.filename = filename
        self.level = level                   #set log level
        self.logger = logging.getLogger()    
        self.logger.setLevel(logging.DEBUG)  #set debug as the lowest logging level
        self.formatter=logging.Formatter("[%(asctime)s] - %(levelname)s : %(message)s")#logging format
 
    def __createFileHandler(self):
        #logging to file
        fh=logging.FileHandler(self.filename,'a')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(self.formatter)
        self.logger.addHandler(fh)
        return fh
    
    def __createStreamHandler(self):
        #logging to console
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(self.formatter)
        self.logger.addHandler(ch)
        return ch
 
    def __console(self,message):
        if self.level == "INFO":
            self.logger.info(message)
        if self.level == "DEBUG":
            self.logger.debug(message)
        if self.level == "WARN":
            self.logger.warning(message)
        if self.level == "ERROR":
            self.logger.error(message)

    def write_log(self, way, level, msg):
        '''write different levels of log with two ways'''
        # way of 'f' -> write log to logfile
        # way of 'c' -> print log on console
        
        self.level = level
        handler = self.__createFileHandler() if way == 'f' else self.__createStreamHandler()
        self.__console(msg)
        self.logger.removeHandler(handler)

    def log_c_and_f(self, level, msg):
        self.write_log('f', level, msg)
        self.write_log('c', level, msg)
# some examples of an instance using the class
# logcase = Log('test.log')
# logcase.write_log('f','WARN','Today is gonna be a bad day!')
# logcase.write_log('c','WARN','Today is gonna be a bad day!')
# logcase.write_log('c','INFO','Today is gonna be a good day!')
# logcase.write_log('f','INFO','Today is gonna be a good day!')
