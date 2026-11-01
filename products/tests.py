from decimal import Decimal
from django.test import TestCase
from products.models import Product


class ProductManagementTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Laptop Stand",
            length=Decimal("25.00"),
            width=Decimal("20.00"),
            height=Decimal("5.00"),
            weight=Decimal("0.80")
        )

    def test_product_list_view(self):
        """Verify product catalog table displays product name, dimensions, and weight."""
        response = self.client.get('/products/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Laptop Stand")
        self.assertContains(response, "25.00")
        self.assertContains(response, "20.00")
        self.assertContains(response, "5.00")
        self.assertContains(response, "0.80 kg")

    def test_product_create_view_success(self):
        """Verify adding a new product via form saves to database."""
        post_data = {
            'name': 'Wireless Charger',
            'length': '10.00',
            'width': '10.00',
            'height': '1.50',
            'weight': '0.20',
        }
        response = self.client.post('/products/create/', post_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Product.objects.filter(name='Wireless Charger').exists())

    def test_product_create_invalid_negative_dimensions(self):
        """Verify validation error when dimensions are negative."""
        post_data = {
            'name': 'Invalid Negative Length',
            'length': '-5.00',
            'width': '10.00',
            'height': '2.00',
            'weight': '0.50',
        }
        response = self.client.post('/products/create/', post_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Product.objects.filter(name='Invalid Negative Length').exists())
        self.assertContains(response, "greater than zero")

    def test_product_create_invalid_zero_dimension(self):
        """Verify validation error when dimension is zero."""
        post_data = {
            'name': 'Zero Width Product',
            'length': '10.00',
            'width': '0.00',
            'height': '2.00',
            'weight': '0.50',
        }
        response = self.client.post('/products/create/', post_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Product.objects.filter(name='Zero Width Product').exists())
        self.assertContains(response, "greater than zero")

    def test_product_create_invalid_negative_weight(self):
        """Verify validation error when weight is negative."""
        post_data = {
            'name': 'Negative Weight Product',
            'length': '10.00',
            'width': '10.00',
            'height': '2.00',
            'weight': '-0.50',
        }
        response = self.client.post('/products/create/', post_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Product.objects.filter(name='Negative Weight Product').exists())
        self.assertContains(response, "greater than zero")

    def test_product_update_view(self):
        """Verify editing product details updates database values."""
        post_data = {
            'name': 'Laptop Stand Pro',
            'length': '28.00',
            'width': '22.00',
            'height': '6.00',
            'weight': '0.95',
        }
        response = self.client.post(f'/products/{self.product.pk}/edit/', post_data)
        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Laptop Stand Pro')
        self.assertEqual(self.product.length, Decimal('28.00'))

    def test_product_delete_confirm_page(self):
        """Verify GET request to delete view renders confirmation page."""
        response = self.client.get(f'/products/{self.product.pk}/delete/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Confirm Product Deletion")
        self.assertContains(response, self.product.name)

    def test_product_delete_view(self):
        """Verify POST request to delete view removes product."""
        response = self.client.post(f'/products/{self.product.pk}/delete/')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())
