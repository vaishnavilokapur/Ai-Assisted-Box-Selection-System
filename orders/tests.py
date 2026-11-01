from decimal import Decimal
from django.test import TestCase

from boxes.models import Box
from orders.models import Order, OrderItem
from orders.services import check_box_overlap, recommend_box_for_order
from products.models import Product


class PackWiseRecommendationAlgorithmTests(TestCase):
    """
    Automated tests verifying the PackWise box recommendation algorithm.
    """

    def setUp(self):
        # Create standard catalog boxes for testing
        self.box_small = Box.objects.create(
            name="Box Small",
            length=Decimal("15.00"),
            width=Decimal("15.00"),
            height=Decimal("15.00"),
            max_weight=Decimal("3.00"),
            cost=Decimal("20.00")
        )
        self.box_medium = Box.objects.create(
            name="Box Medium",
            length=Decimal("30.00"),
            width=Decimal("20.00"),
            height=Decimal("15.00"),
            max_weight=Decimal("10.00"),
            cost=Decimal("45.00")
        )
        self.box_large = Box.objects.create(
            name="Box Large",
            length=Decimal("50.00"),
            width=Decimal("40.00"),
            height=Decimal("30.00"),
            max_weight=Decimal("25.00"),
            cost=Decimal("90.00")
        )

    def test_single_product_fitting_in_box(self):
        """
        1. Test a single product fitting normally inside a suitable box.
        """
        product = Product.objects.create(
            name="Standard Mug",
            length=Decimal("10.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            weight=Decimal("0.50")
        )
        order = Order.objects.create(order_number="ORD-SINGLE-01")
        OrderItem.objects.create(order=order, product=product, quantity=1)

        result = recommend_box_for_order(order)

        self.assertTrue(result['success'])
        self.assertEqual(result['box'], self.box_small)
        self.assertEqual(result['total_weight'], Decimal("0.50"))
        self.assertEqual(len(result['placements']), 1)

        # Confirm placement stays within box bounds
        placement = result['placements'][0]
        px, py, pz = placement['position']
        dx, dy, dz = placement['dimensions']
        self.assertLessEqual(px + dx, float(self.box_small.length))
        self.assertLessEqual(py + dy, float(self.box_small.width))
        self.assertLessEqual(pz + dz, float(self.box_small.height))

    def test_product_fitting_only_after_rotation(self):
        """
        2. Test a product that fits inside a box only when rotated.
        Product original dimensions: (5.00 x 25.00 x 8.00 cm).
        Box dimensions: (26.00 x 12.00 x 10.00 cm).
        In original orientation: width 25.00 > box width 12.00 (would fail).
        Rotated to (25.00 x 8.00 x 5.00 cm): fits completely.
        """
        special_box = Box.objects.create(
            name="Special Slender Box",
            length=Decimal("26.00"),
            width=Decimal("12.00"),
            height=Decimal("10.00"),
            max_weight=Decimal("5.00"),
            cost=Decimal("25.00")
        )
        long_tool = Product.objects.create(
            name="Hand Saw",
            length=Decimal("5.00"),
            width=Decimal("25.00"),
            height=Decimal("8.00"),
            weight=Decimal("1.20")
        )
        order = Order.objects.create(order_number="ORD-ROT-01")
        OrderItem.objects.create(order=order, product=long_tool, quantity=1)

        result = recommend_box_for_order(order)

        self.assertTrue(result['success'])
        # Small box (15x15x15) cannot fit length 25. Special Slender Box fits with rotation.
        self.assertEqual(result['box'], special_box)

        # Verify the placed dimensions respect box boundary
        placement = result['placements'][0]
        px, py, pz = placement['position']
        dx, dy, dz = placement['dimensions']
        self.assertLessEqual(px + dx, float(special_box.length))
        self.assertLessEqual(py + dy, float(special_box.width))
        self.assertLessEqual(pz + dz, float(special_box.height))

    def test_multiple_products_with_different_quantities(self):
        """
        3. Test multiple products with different quantities being packed together.
        """
        prod_a = Product.objects.create(
            name="Perfume Bottle",
            length=Decimal("5.00"),
            width=Decimal("5.00"),
            height=Decimal("5.00"),
            weight=Decimal("0.20")
        )
        prod_b = Product.objects.create(
            name="Face Cream",
            length=Decimal("8.00"),
            width=Decimal("5.00"),
            height=Decimal("5.00"),
            weight=Decimal("0.35")
        )

        order = Order.objects.create(order_number="ORD-MULTI-QTY-01")
        OrderItem.objects.create(order=order, product=prod_a, quantity=3)  # 3 * 0.20 = 0.60 kg
        OrderItem.objects.create(order=order, product=prod_b, quantity=2)  # 2 * 0.35 = 0.70 kg

        result = recommend_box_for_order(order)

        self.assertTrue(result['success'])
        # Total weight: 1.30 kg
        self.assertEqual(result['total_weight'], Decimal("1.30"))
        # 3 + 2 = 5 items total
        self.assertEqual(result['items_count'], 5)
        self.assertEqual(len(result['placements']), 5)

        # Verify no two products overlap in 3D coordinates
        placements = result['placements']
        for i in range(len(placements)):
            box1 = (
                placements[i]['position'][0], placements[i]['position'][1], placements[i]['position'][2],
                placements[i]['dimensions'][0], placements[i]['dimensions'][1], placements[i]['dimensions'][2]
            )
            for j in range(i + 1, len(placements)):
                box2 = (
                    placements[j]['position'][0], placements[j]['position'][1], placements[j]['position'][2],
                    placements[j]['dimensions'][0], placements[j]['dimensions'][1], placements[j]['dimensions'][2]
                )
                self.assertFalse(
                    check_box_overlap(box1, box2),
                    f"Placements {i} and {j} overlap!"
                )

    def test_weight_exceeding_box_capacity(self):
        """
        4. Test that a box with sufficient volume is rejected if total weight
        exceeds its maximum weight capacity.
        """
        heavy_weight = Product.objects.create(
            name="Cast Iron Dumbbell",
            length=Decimal("12.00"),
            width=Decimal("12.00"),
            height=Decimal("12.00"),
            weight=Decimal("4.50")
        )
        order = Order.objects.create(order_number="ORD-OVERWEIGHT-01")
        OrderItem.objects.create(order=order, product=heavy_weight, quantity=1)

        result = recommend_box_for_order(order)

        self.assertTrue(result['success'])
        # Box Small volume (3375) fits the item (1728), but max_weight is 3.0 kg < 4.5 kg.
        # Box Medium (max_weight 10.0 kg) must be selected instead.
        self.assertEqual(result['box'], self.box_medium)

    def test_products_not_physically_fitting_or_overlapping(self):
        """
        5. Test when products physically cannot fit or would exceed the volume/boundaries
        of all available boxes without overlapping.
        """
        giant_appliance = Product.objects.create(
            name="Refrigerator Unit",
            length=Decimal("80.00"),
            width=Decimal("70.00"),
            height=Decimal("180.00"),
            weight=Decimal("75.00")
        )
        order = Order.objects.create(order_number="ORD-OVERSIZED-01")
        OrderItem.objects.create(order=order, product=giant_appliance, quantity=1)

        result = recommend_box_for_order(order)

        self.assertFalse(result['success'])
        self.assertIsNone(result['box'])
        self.assertIn("No available box can accommodate", result['message'])

    def test_selection_of_cheapest_box_when_volumes_are_equal(self):
        """
        6. Test that when two boxes have the exact same volume and fit the order,
        the one with the lowest cost is selected.
        """
        # Two boxes of identical volume: 20 * 20 * 20 = 8000 cm3
        box_expensive = Box.objects.create(
            name="Deluxe Cube Box",
            length=Decimal("20.00"),
            width=Decimal("20.00"),
            height=Decimal("20.00"),
            max_weight=Decimal("15.00"),
            cost=Decimal("60.00")
        )
        box_budget = Box.objects.create(
            name="Budget Cube Box",
            length=Decimal("20.00"),
            width=Decimal("20.00"),
            height=Decimal("20.00"),
            max_weight=Decimal("15.00"),
            cost=Decimal("35.00")
        )

        item = Product.objects.create(
            name="Desktop Speaker",
            length=Decimal("16.00"),
            width=Decimal("16.00"),
            height=Decimal("16.00"),
            weight=Decimal("2.50")
        )
        order = Order.objects.create(order_number="ORD-TIE-BREAK-01")
        OrderItem.objects.create(order=order, product=item, quantity=1)

        result = recommend_box_for_order(order)

        self.assertTrue(result['success'])
        # Box Small (15x15x15) and Medium (30x20x15: height 16 > 15) cannot fit.
        # Between Deluxe (INR 60) and Budget (INR 35), Budget must be chosen.
        self.assertEqual(result['box'], box_budget)

    def test_empty_order(self):
        """
        7. Test that an order with no products returns a clear and descriptive message.
        """
        empty_order = Order.objects.create(order_number="ORD-EMPTY-TEST-01")

        result = recommend_box_for_order(empty_order)

        self.assertFalse(result['success'])
        self.assertIsNone(result['box'])
        self.assertEqual(result['items_count'], 0)
        self.assertIn("has no products to pack", result['message'])

    def test_box_with_invalid_dimensions_skipped(self):
        """
        8. Test that boxes with non-positive dimensions or weights are safely skipped.
        """
        invalid_box = Box.objects.create(
            name="Corrupted Zero Dimension Box",
            length=Decimal("0.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            max_weight=Decimal("5.00"),
            cost=Decimal("5.00")
        )
        product = Product.objects.create(
            name="Small Toy",
            length=Decimal("5.00"),
            width=Decimal("5.00"),
            height=Decimal("5.00"),
            weight=Decimal("0.10")
        )
        order = Order.objects.create(order_number="ORD-INVALID-BOX-01")
        OrderItem.objects.create(order=order, product=product, quantity=1)

        result = recommend_box_for_order(order)

        self.assertTrue(result['success'])
        # The zero dimension box must be skipped, selecting valid Box Small instead
        self.assertNotEqual(result['box'], invalid_box)
        self.assertEqual(result['box'], self.box_small)


class OrderWebFlowTests(TestCase):
    """
    Tests for web order creation, form validation, and recommendation presentation.
    """

    def setUp(self):
        self.box = Box.objects.create(
            name="Delivery Box A",
            length=Decimal("25.00"),
            width=Decimal("20.00"),
            height=Decimal("15.00"),
            max_weight=Decimal("5.00"),
            cost=Decimal("35.00")
        )
        self.product1 = Product.objects.create(
            name="Wireless Mouse",
            length=Decimal("12.00"),
            width=Decimal("7.00"),
            height=Decimal("4.00"),
            weight=Decimal("0.15")
        )
        self.product2 = Product.objects.create(
            name="Coffee Mug",
            length=Decimal("10.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            weight=Decimal("0.40")
        )

    def test_order_create_get_view(self):
        """GET /orders/create/ loads the order creation page."""
        response = self.client.get('/orders/create/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create Packaging Order")
        self.assertContains(response, "Wireless Mouse")

    def test_order_create_post_success(self):
        """POST /orders/create/ saves Order and OrderItems and redirects to recommendation."""
        post_data = {
            'order_number': 'ORD-WEB-001',
            'product_id': [str(self.product1.id), str(self.product2.id)],
            'quantity': ['2', '1']
        }
        response = self.client.post('/orders/create/', post_data)
        self.assertEqual(response.status_code, 302)

        order = Order.objects.get(order_number='ORD-WEB-001')
        self.assertRedirects(response, f'/orders/{order.id}/recommendation/')
        self.assertEqual(order.items.count(), 2)

        item1 = order.items.get(product=self.product1)
        self.assertEqual(item1.quantity, 2)
        item2 = order.items.get(product=self.product2)
        self.assertEqual(item2.quantity, 1)

    def test_order_create_no_products_validation_error(self):
        """POST without any selected products returns a validation error."""
        post_data = {
            'order_number': 'ORD-EMPTY-FAIL',
        }
        response = self.client.post('/orders/create/', post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please select at least one product")
        self.assertFalse(Order.objects.filter(order_number='ORD-EMPTY-FAIL').exists())

    def test_order_create_invalid_quantity_validation_error(self):
        """POST with zero or negative quantity returns validation error."""
        post_data = {
            'order_number': 'ORD-NEG-QTY',
            'product_id': [str(self.product1.id)],
            'quantity': ['0']
        }
        response = self.client.post('/orders/create/', post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "positive integers")
        self.assertFalse(Order.objects.filter(order_number='ORD-NEG-QTY').exists())

    def test_order_create_single_product_web_flow(self):
        """Verify creating an order with one product saves accurately via web flow."""
        post_data = {
            'order_number': 'ORD-SINGLE-WEB',
            'product_id': [str(self.product1.id)],
            'quantity': ['3']
        }
        response = self.client.post('/orders/create/', post_data)
        self.assertEqual(response.status_code, 302)
        order = Order.objects.get(order_number='ORD-SINGLE-WEB')
        self.assertEqual(order.items.count(), 1)
        item = order.items.first()
        self.assertEqual(item.product, self.product1)
        self.assertEqual(item.quantity, 3)

    def test_dashboard_and_order_list_views(self):
        """Verify Dashboard and Orders List endpoints respond with HTTP 200."""
        # Dashboard
        res_home = self.client.get('/')
        self.assertEqual(res_home.status_code, 200)
        self.assertContains(res_home, "PackWise")
        self.assertContains(res_home, "Dashboard")

        # Orders List
        res_list = self.client.get('/orders/')
        self.assertEqual(res_list.status_code, 200)
        self.assertContains(res_list, "Packaging Orders")

    def test_recommendation_result_view(self):
        """GET /orders/<id>/recommendation/ displays all required fields."""
        order = Order.objects.create(order_number='ORD-RESULT-VIEW')
        OrderItem.objects.create(order=order, product=self.product1, quantity=2)

        response = self.client.get(f'/orders/{order.id}/recommendation/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ORD-RESULT-VIEW")
        self.assertContains(response, "Wireless Mouse")
        self.assertContains(response, "Delivery Box A")
        self.assertContains(response, "25.00")
        self.assertContains(response, "35.00")

