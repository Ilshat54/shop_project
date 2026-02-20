from django.test import TestCase

# Create your tests here.
"""
Тесты для приложения shop_project
Покрытие: модели Category, Product и основные представления
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from main.models import Category, Product, User

class CategoryModelTest(TestCase):
    """
    Тесты для модели Category
    """
    
    def setUp(self):
        """Создаем тестовые данные перед каждым тестом"""
        self.category = Category.objects.create(
            name="Тестовая категория",
            image="img/test.png"
        )
    
    def test_category_creation(self):
        """Тест: создание категории работает корректно"""
        # Проверяем, что категория создалась
        self.assertEqual(self.category.name, "Тестовая категория")
        self.assertEqual(self.category.image, "img/test.png")
        self.assertIsNotNone(self.category.category_id)
    
    def test_category_str_method(self):
        """Тест: строковое представление категории возвращает ее название"""
        self.assertEqual(str(self.category), "Тестовая категория")
    
    def test_category_id_property(self):
        """Тест: свойство id возвращает category_id"""
        self.assertEqual(self.category.id, self.category.category_id)


class ProductModelTest(TestCase):
    """
    Тесты для модели Product
    """
    
    def setUp(self):
        """Создаем категорию и товар для тестов"""
        self.category = Category.objects.create(
            name="Категория для товаров",
            image="img/test.png"
        )
        self.product = Product.objects.create(
            name="Тестовый товар",
            description="Описание тестового товара",
            characteristics="Характеристики",
            price=999.99,
            stock_quantity=10,
            category=self.category,
            image="img/product.png"
        )
    
    def test_product_creation(self):
        """Тест: создание товара работает корректно"""
        self.assertEqual(self.product.name, "Тестовый товар")
        self.assertEqual(self.product.price, 999.99)
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(self.product.stock_quantity, 10)
    
    def test_product_str_method(self):
        """Тест: строковое представление товара возвращает его название"""
        self.assertEqual(str(self.product), "Тестовый товар")
    
    def test_product_category_relation(self):
        """Тест: связь товара с категорией работает"""
        # Получаем товары по категории
        products_in_category = Product.objects.filter(category=self.category)
        self.assertIn(self.product, products_in_category)
        self.assertEqual(products_in_category.count(), 1)


class UserModelTest(TestCase):
    """
    Тесты для модели User (кастомная модель)
    """
    
    def setUp(self):
        """Создаем тестового пользователя"""
        self.user = User.objects.create(
            name="Тестовый Пользователь",
            email="test@example.com",
            password=make_password("testpass123"),
            is_admin=False
        )
    
    def test_user_creation(self):
        """Тест: создание пользователя работает корректно"""
        self.assertEqual(self.user.name, "Тестовый Пользователь")
        self.assertEqual(self.user.email, "test@example.com")
        self.assertFalse(self.user.is_admin)
    
    def test_user_str_method(self):
        """Тест: строковое представление пользователя возвращает его имя"""
        self.assertEqual(str(self.user), "Тестовый Пользователь")
    
    def test_user_email_unique(self):
        """Тест: email должен быть уникальным"""
        with self.assertRaises(Exception):
            User.objects.create(
                name="Другой пользователь",
                email="test@example.com",  # Тот же email
                password="password"
            )


class ViewsTestCase(TestCase):
    """
    Интеграционные тесты для представлений (views)
    """
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.client = Client()
        
        # Создаем категорию
        self.category = Category.objects.create(
            name="Тестовая категория",
            image="img/test.png"
        )
        
        # Создаем товар
        self.product = Product.objects.create(
            name="Тестовый товар",
            description="Описание",
            price=1000.00,
            stock_quantity=5,
            category=self.category,
            image="img/product.png"
        )
    
    def test_index_view_status_code(self):
        """Тест: главная страница доступна (код 200)"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_index_view_uses_correct_template(self):
        """Тест: главная страница использует правильный шаблон"""
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'main/index.html')
    
    def test_index_view_context_contains_categories(self):
        """Тест: контекст главной страницы содержит категории"""
        response = self.client.get('/')
        self.assertIn('categories', response.context)
        self.assertEqual(len(response.context['categories']), 1)
        self.assertEqual(response.context['categories'][0].name, "Тестовая категория")
    
    def test_category_view(self):
        """Тест: страница категории отображает товары"""
        response = self.client.get(f'/category/{self.category.category_id}/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('products', response.context)
        self.assertEqual(len(response.context['products']), 1)
    
    def test_product_view(self):
        """Тест: страница товара отображает его данные"""
        response = self.client.get(f'/product/{self.product.product_id}/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('product', response.context)
        self.assertEqual(response.context['product'].name, "Тестовый товар")
    
    def test_register_view_get(self):
        """Тест: GET запрос на регистрацию возвращает форму"""
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/register.html')
    
    def test_register_view_post_success(self):
        """Тест: POST запрос с корректными данными создает пользователя"""
        user_data = {
            'name': 'Новый Пользователь',
            'email': 'newuser@example.com',
            'password': 'securepassword123'
        }
        response = self.client.post('/register/', user_data)
        
        # Проверяем, что пользователь создался
        self.assertEqual(User.objects.filter(email='newuser@example.com').count(), 1)
        
        # Проверяем, что после успешной регистрации происходит редирект
        self.assertEqual(response.status_code, 302)
    
    def test_register_view_post_duplicate_email(self):
        """Тест: попытка регистрации с существующим email вызывает ошибку"""
        # Создаем пользователя
        User.objects.create(
            name="Существующий",
            email="existing@example.com",
            password="password"
        )
        
        # Пытаемся зарегистрироваться с тем же email
        user_data = {
            'name': 'Новый',
            'email': 'existing@example.com',
            'password': 'password123'
        }
        response = self.client.post('/register/', user_data, follow=True)
        
        # Проверяем, что сообщение об ошибке присутствует
        messages = list(response.context['messages'])
        self.assertTrue(any("уже зарегистрирован" in str(msg) for msg in messages))


class ProductSearchTest(TestCase):
    """
    Тесты для поиска товаров
    """
    
    def setUp(self):
        """Создаем товары для тестирования поиска"""
        self.category = Category.objects.create(name="Техника")
        
        Product.objects.create(
            name="Холодильник LG",
            description="Большой холодильник",
            price=45000,
            stock_quantity=5,
            category=self.category,
            image="img/lg_fridge.png"
        )
        
        Product.objects.create(
            name="Телевизор Samsung",
            description="4K телевизор",
            price=38000,
            stock_quantity=3,
            category=self.category,
            image="img/samsung_tv.png"
        )
    
    def test_search_by_name(self):
        """Тест: поиск по названию работает"""
        response = self.client.get('/?q=Холодильник')
        self.assertContains(response, "Холодильник LG")
        self.assertNotContains(response, "Телевизор Samsung")
    
    def test_search_by_description(self):
        """Тест: поиск по описанию работает"""
        response = self.client.get('/?q=4K')
        self.assertContains(response, "Телевизор Samsung")
        self.assertNotContains(response, "Холодильник LG")
    
    def test_search_empty_result(self):
        """Тест: поиск без результатов не вызывает ошибок"""
        response = self.client.get('/?q=НесуществующийТовар')
        self.assertEqual(response.status_code, 200)
from .tests_failing import *
