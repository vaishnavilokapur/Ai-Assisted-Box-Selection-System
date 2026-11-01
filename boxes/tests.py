from decimal import Decimal
from django.test import TestCase
from boxes.models import Box


class BoxManagementTests(TestCase):
    def setUp(self):
        self.box = Box.objects.create(
            name="Postal Box",
            length=Decimal("20.00"),
            width=Decimal("15.00"),
            height=Decimal("10.00"),
            max_weight=Decimal("5.00"),
            cost=Decimal("25.00")
        )

    def test_box_list_view(self):
        """Verify boxes table displays name, dimensions, max weight, and cost in INR."""
        response = self.client.get('/boxes/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Postal Box")
        self.assertContains(response, "20.00")
        self.assertContains(response, "15.00")
        self.assertContains(response, "10.00")
        self.assertContains(response, "5.00 kg")
        self.assertContains(response, "25.00")

    def test_multiple_boxes_with_different_dimensions_and_costs(self):
        """Verify multiple boxes can be created with varied dimensions and costs."""
        b1 = Box.objects.create(
            name="Mini Parcel",
            length=Decimal("10.00"),
            width=Decimal("10.00"),
            height=Decimal("5.00"),
            max_weight=Decimal("1.50"),
            cost=Decimal("15.00")
        )
        b2 = Box.objects.create(
            name="Jumbo Crate",
            length=Decimal("60.00"),
            width=Decimal("50.00"),
            height=Decimal("40.00"),
            max_weight=Decimal("30.00"),
            cost=Decimal("120.00")
        )
        response = self.client.get('/boxes/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mini Parcel")
        self.assertContains(response, "Jumbo Crate")
        self.assertContains(response, "15.00")
        self.assertContains(response, "120.00")

    def test_box_create_view_success(self):
        """Verify creating a box via form saves to database."""
        post_data = {
            'name': 'Mini Box',
            'length': '12.00',
            'width': '12.00',
            'height': '8.00',
            'max_weight': '2.00',
            'cost': '18.00',
        }
        response = self.client.post('/boxes/create/', post_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Box.objects.filter(name='Mini Box').exists())

    def test_box_create_invalid_negative_dimensions(self):
        """Verify validation error when dimensions are negative."""
        post_data = {
            'name': 'Negative Length Box',
            'length': '-12.00',
            'width': '12.00',
            'height': '8.00',
            'max_weight': '2.00',
            'cost': '18.00',
        }
        response = self.client.post('/boxes/create/', post_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Box.objects.filter(name='Negative Length Box').exists())
        self.assertContains(response, "greater than zero")

    def test_box_create_invalid_zero_weight_capacity(self):
        """Verify validation error when max weight capacity is zero."""
        post_data = {
            'name': 'Zero Weight Box',
            'length': '12.00',
            'width': '12.00',
            'height': '8.00',
            'max_weight': '0.00',
            'cost': '18.00',
        }
        response = self.client.post('/boxes/create/', post_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Box.objects.filter(name='Zero Weight Box').exists())
        self.assertContains(response, "greater than zero")

    def test_box_create_invalid_negative_cost(self):
        """Verify validation error when cost is negative."""
        post_data = {
            'name': 'Negative Cost Box',
            'length': '12.00',
            'width': '12.00',
            'height': '8.00',
            'max_weight': '2.00',
            'cost': '-10.00',
        }
        response = self.client.post('/boxes/create/', post_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Box.objects.filter(name='Negative Cost Box').exists())
        self.assertContains(response, "greater than zero")

    def test_box_update_view(self):
        """Verify editing box updates database values."""
        post_data = {
            'name': 'Postal Box XL',
            'length': '22.00',
            'width': '16.00',
            'height': '12.00',
            'max_weight': '6.00',
            'cost': '29.50',
        }
        response = self.client.post(f'/boxes/{self.box.pk}/edit/', post_data)
        self.assertEqual(response.status_code, 302)
        self.box.refresh_from_db()
        self.assertEqual(self.box.name, 'Postal Box XL')
        self.assertEqual(self.box.cost, Decimal('29.50'))

    def test_box_delete_confirm_page(self):
        """Verify GET request to delete view renders confirmation page."""
        response = self.client.get(f'/boxes/{self.box.pk}/delete/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Confirm Box Deletion")
        self.assertContains(response, self.box.name)

    def test_box_delete_view(self):
        """Verify POST request to delete view removes box."""
        response = self.client.post(f'/boxes/{self.box.pk}/delete/')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Box.objects.filter(pk=self.box.pk).exists())
