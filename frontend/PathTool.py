import sys
import os

'''
Сайд-функция для build приложения. Используется для всех путей к иконкам, при билде.
'''

def resource_path(relative_path):
    """Получает абсолютный путь к ресурсу."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)