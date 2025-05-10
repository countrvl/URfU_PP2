

class WidgetController:
    _instance = None  # Переменная для хранения экземпляра

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WidgetController, cls).__new__(cls)
            cls._instance._widgets = {}  # Словарь зарегистрированных виджетов
        return cls._instance

    def register_widget(self, name, widget):
        """Регистрация виджета"""
        self._widgets[name] = widget

    def get_widget(self, name):
        """Получить виджет по имени"""
        return self._widgets.get(name)

    def call_widget_method(self, widget_name, method_name, *args, **kwargs):
        """
        Вызвать метод у зарегистрированного виджета.
        """
        widget = self.get_widget(widget_name)
        if widget:
            method = getattr(widget, method_name, None)
            if callable(method):
                return method(*args, **kwargs)
            else:
                raise AttributeError(f"'{widget_name}' has no method '{method_name}'")
        else:
            raise ValueError(f"Widget '{widget_name}' not found")
