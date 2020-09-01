import logging
import types


def ml_new_line(self):
    self.handler.setFormatter(self.ml_bformatter)
    self.info('')
    self.handler.setFormatter(self.ml_formatter)


def create_main_logger():

    formatter = logging.Formatter(fmt=u'[%(asctime)s] #%(levelname)-6s [F:%(filename)s L:%(lineno)d] >> %(message)s')
    blank_formatter = logging.Formatter(fmt=u'')

    ml_handler = logging.FileHandler(filename='launcher.engine.log', mode='a')
    ml_handler.setLevel(logging.DEBUG)
    ml_handler.setFormatter(formatter)

    main_logger = logging.getLogger('main_logger')
    main_logger.addHandler(ml_handler)
    main_logger.setLevel(logging.DEBUG)

    main_logger.handler = ml_handler
    main_logger.ml_formatter = formatter
    main_logger.ml_bformatter = blank_formatter
    main_logger.newline = types.MethodType(ml_new_line, main_logger)

    return main_logger
