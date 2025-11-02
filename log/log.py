import logging
import os
import sys
from logging.handlers import RotatingFileHandler

# Папка для логов
LOG_DIR = "./logs"

def setup_logger(process_name=None):
    """
    Настраивает логгер для конкретного процесса
    
    Args:
        process_name: имя процесса ('websocket', 'calling', etc.)
                     Если None - использует имя скрипта
    """
    
    # Определяем имя процесса
    if not process_name:
        # Берём имя скрипта без расширения
        script_name = os.path.basename(sys.argv[0])
        process_name = os.path.splitext(script_name)[0]
    
    # Создаём уникальное имя файла
    pid = os.getpid()
    # log_file = f"{LOG_DIR}/{process_name}_{pid}.log"
    log_file = f"{LOG_DIR}/{process_name}.log"
    
    # Создаём папку если не существует
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # Форматирование
    fmt = logging.Formatter(
        f"%(asctime)s %(levelname)-8s [{process_name}:%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Очищаем существующие хэндлеры (если есть)
    logger = logging.getLogger()
    logger.handlers.clear()
    
    # Обработчик в файл с ротацией
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024, 
        backupCount=50, 
        encoding="utf-8"
    )
    file_handler.setFormatter(fmt)
    
    # Консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(fmt)
    
    # Настраиваем корневой логгер
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info(f"Logger initialized for process '{process_name}' (PID: {pid})")
    
    return logger

# Для обратной совместимости - можно импортировать logger напрямую
# но лучше вызывать setup_logger() в каждом процессе
logger = setup_logger()