"""
Намеренно падающие тесты для демонстрации в лабораторной работе
"""

from django.test import TestCase

class IntentionalFailingTests(TestCase):
    """
    Этот класс содержит тесты, которые специально проваливаются
    для демонстрации работы системы в отчете по ЛР7
    """
    
    def test_intentional_failure_1(self):
        """
        Тест специально проваливается, потому что 1 не равно 2
        Ожидаемый результат: AssertionError
        """
        self.assertEqual(1, 2, "Этот тест создан для демонстрации падения сборки")
    
    def test_intentional_failure_2(self):
        """
        Проверка на заведомо ложное условие
        """
        self.assertTrue(False, "Намеренное падение для отчета")
    
    def test_product_creation_failure(self):
        """
        Демонстрация падения при проверке данных товара
        """
        from main.models import Product
        
        # Создаем товар с некорректными данными (для примера)
        # Этот тест упадет, потому что мы проверяем несуществующее поле
        product = Product.objects.create(
            name="Тестовый товар",
            price=-100,  # Отрицательная цена - ошибка валидации
            stock_quantity=-5  # Отрицательное количество - ошибка
        )
        
        # Проверяем, что цена положительная (это упадет)
        self.assertGreater(product.price, 0, "Цена должна быть положительной")
