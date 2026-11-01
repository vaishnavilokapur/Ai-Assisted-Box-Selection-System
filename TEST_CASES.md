# PackWise – Test Cases Document

This document records the 10 core test cases for the **PackWise AI-Assisted Smart Box Selection System**. All test cases have been verified through automated unit tests executed using Django's test runner (`python manage.py test`).

---

## 1. Test Execution Summary

- **Command:** `python manage.py test`
- **Total Tests in Suite:** 32
- **Pre-execution System Check:** 0 issues identified
- **Execution Time:** ~0.32s
- **Status:** All 32 automated tests passed (0 failures, 0 errors, 0 skipped)

---

## 2. Test Cases Table

| Test Case ID | Test Scenario | Input or Condition | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TC01** | Single product fitting inside a box | Product: "Standard Mug" (10×10×10 cm, 0.50 kg), Qty: 1.<br>Available Boxes: Box Small (15×15×15 cm, max 3.0 kg, ₹20), Box Medium (30×20×15 cm, max 10.0 kg, ₹45), Box Large (50×40×30 cm, max 25.0 kg, ₹90). | Recommendation succeeds (`success=True`). "Box Small" is selected as the smallest suitable box. Item placement stays within box dimensions (10×10×10 cm ≤ 15×15×15 cm). Total weight calculated as 0.50 kg. | `result['success']` is `True`. Recommended box is `Box Small`. Single placement coordinates generated within boundary limits. Total weight is `0.50 kg`. | **PASS** |
| **TC02** | Multiple different products in one order | Product A: "Perfume Bottle" (5×5×5 cm, 0.20 kg, qty 3).<br>Product B: "Face Cream" (8×5×5 cm, 0.35 kg, qty 2).<br>Combined items: 5 units, total weight 1.30 kg. | Recommendation succeeds. All 5 items are packed into a single suitable box without any two items overlapping in 3D coordinate space. | `result['success']` is `True`. All 5 items placed inside box. 3D collision check (`check_box_overlap`) verified `False` for all pairwise placements. Total weight is `1.30 kg`. | **PASS** |
| **TC03** | Multiple quantities of the same product | Product: "Perfume Bottle" (5×5×5 cm, 0.20 kg) with Quantity: 3. | Order expands quantity into 3 individual 3D units. Aggregate weight (0.60 kg) and volume (375 cm³) are computed, and all 3 units are placed without overlap. | `result['items_count']` is `3`. Total weight is `0.60 kg`. 3 distinct non-overlapping placement coordinates generated inside the container. | **PASS** |
| **TC04** | Product rotation during box fitting | Product: "Hand Saw" (5×25×8 cm, 1.20 kg, qty 1).<br>Candidate Box: "Special Slender Box" (26×12×10 cm, max 5.0 kg).<br>*Condition:* In default orientation, width 25 cm > box width 12 cm. Rotated orientation is (25×8×5 cm). | Product is rotated across 6 orthogonal spatial orientations $(L, W, H)$. The rotated orientation fits within box boundaries (25 ≤ 26, 8 ≤ 12, 5 ≤ 10). "Special Slender Box" is recommended. | `result['success']` is `True`. "Special Slender Box" recommended. Placement dimensions reflect rotated coordinates (25×8×5 cm) respecting all boundary dimensions. | **PASS** |
| **TC05** | Product weight exceeding box capacity | Product: "Cast Iron Dumbbell" (12×12×12 cm, 4.50 kg, qty 1).<br>Box Small: 15×15×15 cm, volume 3375 cm³, max weight 3.0 kg.<br>Box Medium: 30×20×15 cm, max weight 10.0 kg. | Although Box Small has sufficient volume (3375 cm³ > 1728 cm³), it is rejected because product weight (4.50 kg) exceeds its 3.0 kg maximum weight capacity. Box Medium is selected instead. | `result['success']` is `True`. Box Small skipped due to weight limit (4.50 kg > 3.00 kg). `result['box']` is `Box Medium`. | **PASS** |
| **TC06** | No suitable box available | Product: "Refrigerator Unit" (80×70×180 cm, 75.0 kg, qty 1).<br>Largest Box in Catalog: Box Large (50×40×30 cm, max weight 25.0 kg). | Recommendation fails (`success=False`, `box=None`). A clear diagnostic message is returned indicating no available box can accommodate the order dimensions and weight. | `result['success']` is `False`. `result['box']` is `None`. Descriptive failure reason returned: *"No available box can accommodate Order..."*. | **PASS** |
| **TC07** | Empty order validation | Order created with 0 items (`OrderItem` count = 0), or order form submitted without selecting any products. | Backend recommendation service returns failure with descriptive message. Web order form rejects submission and displays validation error: *"Please select at least one product."* | `result['success']` is `False`, message contains *"has no products to pack"*. In web view, form validation prevents order creation with status code 200. | **PASS** |
| **TC08** | Lowest-cost suitable box selection | Item: "Desktop Speaker" (16×16×16 cm, 2.50 kg).<br>Two boxes of identical volume (20×20×20 cm = 8000 cm³, max weight 15.0 kg):<br>- "Deluxe Cube Box" (Cost: ₹60.00)<br>- "Budget Cube Box" (Cost: ₹35.00) | Both boxes physically fit the product and support its weight. The service evaluates cost as the tie-breaker and selects the cheaper box ("Budget Cube Box"). | `result['success']` is `True`. `result['box']` is `Budget Cube Box` (cost `Decimal("35.00")`), choosing the lowest-cost suitable option. | **PASS** |
| **TC09** | Invalid product dimensions or weight | Web form submission with invalid inputs:<br>- Length: `-5.00 cm`<br>- Width: `0.00 cm`<br>- Weight: `-0.50 kg` | Product form validation rejects negative and zero values. Database record is not saved. Form displays error message: *"Length/Width/Height/Weight must be greater than zero."* | Form submission returns HTTP 200 with validation errors. No invalid `Product` record is created in the database. | **PASS** |
| **TC10** | Invalid box dimensions or weight capacity | Web form submission and service evaluation:<br>- Length: `-12.00 cm`<br>- Max weight: `0.00 kg`<br>- Cost: `-18.00`<br>- Database record with zero dimensions. | Form validation rejects negative/zero inputs with *"must be greater than zero"*. When a corrupted box exists in the database, the recommendation service logs and skips it during evaluation. | Form rejects invalid inputs with validation errors. Recommendation algorithm skips corrupted zero-dimension boxes and recommends a valid box. | **PASS** |

---

## 3. Mapping to Automated Test Suite

| Test Case ID | Implementing Test Class | Test Method Name |
| :--- | :--- | :--- |
| **TC01** | `orders.tests.PackWiseRecommendationAlgorithmTests` | `test_single_product_fitting_in_box` |
| **TC02** | `orders.tests.PackWiseRecommendationAlgorithmTests` | `test_multiple_products_with_different_quantities` |
| **TC03** | `orders.tests.PackWiseRecommendationAlgorithmTests` | `test_multiple_products_with_different_quantities` |
| **TC04** | `orders.tests.PackWiseRecommendationAlgorithmTests` | `test_product_fitting_only_after_rotation` |
| **TC05** | `orders.tests.PackWiseRecommendationAlgorithmTests` | `test_weight_exceeding_box_capacity` |
| **TC06** | `orders.tests.PackWiseRecommendationAlgorithmTests` | `test_products_not_physically_fitting_or_overlapping` |
| **TC07** | `orders.tests.PackWiseRecommendationAlgorithmTests`<br>`orders.tests.OrderWebFlowTests` | `test_empty_order`<br>`test_order_create_no_products_validation_error` |
| **TC08** | `orders.tests.PackWiseRecommendationAlgorithmTests` | `test_selection_of_cheapest_box_when_volumes_are_equal` |
| **TC09** | `products.tests.ProductManagementTests` | `test_product_create_invalid_negative_dimensions`<br>`test_product_create_invalid_zero_dimension`<br>`test_product_create_invalid_negative_weight` |
| **TC10** | `boxes.tests.BoxManagementTests`<br>`orders.tests.PackWiseRecommendationAlgorithmTests` | `test_box_create_invalid_negative_dimensions`<br>`test_box_create_invalid_zero_weight_capacity`<br>`test_box_create_invalid_negative_cost`<br>`test_box_with_invalid_dimensions_skipped` |
