import logging
import os


def configure_logger():
    # get environment variable LOG_LEVEL
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()

    # configure logging
    logging.basicConfig(
        # to use colors without colorama
        level=logging.INFO,
        format="%(levelname)s %(message)s",
        handlers=[],
    )

    try:
        import colorama

        colorama.init()
        from colorama import Fore, Style

        class ColorFormatter(logging.Formatter):
            def format(self, record):
                if record.levelno == logging.WARNING:
                    record.msg = Fore.YELLOW + record.msg + Style.RESET_ALL
                elif record.levelno == logging.ERROR:
                    record.msg = Fore.RED + record.msg + Style.RESET_ALL
                elif record.levelno == logging.INFO:
                    record.msg = Fore.GREEN + record.msg + Style.RESET_ALL
                return super().format(record)

        color_formatter = ColorFormatter("%(levelname)s %(message)s")
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(color_formatter)
        logging.getLogger().addHandler(console_handler)
        logging.getLogger().setLevel(log_level)
    except ImportError:
        pass  # expected if colorama is not installed - logging will be without colors


# Configure logger
configure_logger()
logger = logging.getLogger()
