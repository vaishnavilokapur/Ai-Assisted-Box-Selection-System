

from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple, Union

from boxes.models import Box
from orders.models import Order, OrderItem
from products.models import Product


def get_orientations(length: float, width: float, height: float) -> List[Tuple[float, float, float]]:
    """
    Generate all six 3D spatial orientations for a product:
    (L, W, H), (L, H, W), (W, L, H), (W, H, L), (H, L, W), (H, W, L).
    Returns unique orientations to avoid redundant checks.
    """
    l, w, h = float(length), float(width), float(height)
    all_six = [
        (l, w, h),
        (l, h, w),
        (w, l, h),
        (w, h, l),
        (h, l, w),
        (h, w, l),
    ]

    # Preserve order while deduplicating identical orientations (e.g. for cubes)
    unique_orientations: List[Tuple[float, float, float]] = []
    seen = set()
    for orient in all_six:
        if orient not in seen:
            seen.add(orient)
            unique_orientations.append(orient)

    return unique_orientations


def check_box_overlap(
    box1: Tuple[float, float, float, float, float, float],
    box2: Tuple[float, float, float, float, float, float]
) -> bool:
    """
    Determines if two 3D rectangular bounding boxes overlap in space.
    Each box is defined as: (x, y, z, dx, dy, dz)
    Where (x, y, z) is the origin corner and (dx, dy, dz) are the dimensions.
    """
    x1, y1, z1, dx1, dy1, dz1 = box1
    x2, y2, z2, dx2, dy2, dz2 = box2

    # Boxes overlap only if they overlap across all three spatial dimensions
    overlap_x = (x1 < x2 + dx2) and (x1 + dx1 > x2)
    overlap_y = (y1 < y2 + dy2) and (y1 + dy1 > y2)
    overlap_z = (z1 < z2 + dz2) and (z1 + dz1 > z2)

    return overlap_x and overlap_y and overlap_z


def point_inside_any_placed_item(
    x: float, y: float, z: float,
    placed_items: List[Dict[str, Any]]
) -> bool:
    """
    Checks whether candidate coordinate (x, y, z) falls strictly inside
    an already placed box.
    """
    for item in placed_items:
        bx, by, bz = item['position']
        bdx, bdy, bdz = item['dimensions']
        if (bx <= x < bx + bdx) and (by <= y < by + bdy) and (bz <= z < bz + bdz):
            return True
    return False


def simulate_3d_pack(
    items_to_pack: List[Dict[str, Any]],
    box_l: float,
    box_w: float,
    box_h: float
) -> Optional[List[Dict[str, Any]]]:
    """
    Simulates packing a list of rectangular items into a box using
    corner-point placement with full 6-degree orientation testing.

    Ensures:
    - Products stay completely inside box boundaries (0 <= x + dx <= box_l, etc.)
    - No two products overlap in 3D space.
    """
    placed_items: List[Dict[str, Any]] = []
    # Candidate placement corners (x, y, z), starting at bottom-left-front (0, 0, 0)
    candidate_points: List[Tuple[float, float, float]] = [(0.0, 0.0, 0.0)]

    for item in items_to_pack:
        dims = item['original_dims']
        orientations = get_orientations(dims[0], dims[1], dims[2])
        placed = False

        # Sort candidate anchor points: lowest height (z), lowest depth (y), lowest width (x)
        candidate_points.sort(key=lambda pt: (pt[2], pt[1], pt[0]))

        for pt in list(candidate_points):
            px, py, pz = pt

            for dx, dy, dz in orientations:
                # 1. Boundary check: Product must fit completely inside the box
                if (px + dx > box_l) or (py + dy > box_w) or (pz + dz > box_h):
                    continue

                new_box = (px, py, pz, dx, dy, dz)

                # 2. Overlap check: Product must not collide with any already placed item
                has_overlap = any(
                    check_box_overlap(new_box, (
                        p['position'][0], p['position'][1], p['position'][2],
                        p['dimensions'][0], p['dimensions'][1], p['dimensions'][2]
                    ))
                    for p in placed_items
                )

                if not has_overlap:
                    # Item fits at this position and orientation
                    placed_items.append({
                        'product_id': item['product_id'],
                        'product_name': item['product_name'],
                        'position': (px, py, pz),
                        'dimensions': (dx, dy, dz),
                    })

                    # Remove the used anchor point
                    if pt in candidate_points:
                        candidate_points.remove(pt)

                    # Generate new anchor candidate points adjacent to this placed item
                    new_candidates = [
                        (px + dx, py, pz),
                        (px, py + dy, pz),
                        (px, py, pz + dz)
                    ]

                    for c in new_candidates:
                        # Only keep candidate points that are within box boundaries
                        if c[0] < box_l and c[1] < box_w and c[2] < box_h:
                            if not point_inside_any_placed_item(c[0], c[1], c[2], placed_items):
                                if c not in candidate_points:
                                    candidate_points.append(c)

                    placed = True
                    break

            if placed:
                break

        if not placed:
            # Item could not be accommodated in this box
            return None

    return placed_items


def can_fit_in_box(
    items_to_pack: List[Dict[str, Any]],
    box: Box
) -> Optional[List[Dict[str, Any]]]:
    """
    Evaluates whether all items fit in the given box across multiple sorting
    heuristics (Decreasing Volume, Decreasing Max Dimension, Decreasing Footprint).
    """
    box_l = float(box.length)
    box_w = float(box.width)
    box_h = float(box.height)
    box_volume = box_l * box_w * box_h

    # Fast volume check: Total item volume cannot exceed box volume
    total_items_volume = sum(item['volume'] for item in items_to_pack)
    if total_items_volume > box_volume:
        return None

    # Fast individual dimension check:
    # Every item's smallest dimension must be <= the box's smallest dimension
    box_min_dim = min(box_l, box_w, box_h)
    for item in items_to_pack:
        if min(item['original_dims']) > box_min_dim:
            return None

    # Try 3 packing heuristic sorting orders:
    sorting_strategies = [
        # 1. Largest volume first
        sorted(items_to_pack, key=lambda it: it['volume'], reverse=True),
        # 2. Longest single dimension first
        sorted(items_to_pack, key=lambda it: max(it['original_dims']), reverse=True),
        # 3. Largest footprint (L * W) first
        sorted(items_to_pack, key=lambda it: it['original_dims'][0] * it['original_dims'][1], reverse=True),
    ]

    for sorted_items in sorting_strategies:
        result = simulate_3d_pack(sorted_items, box_l, box_w, box_h)
        if result is not None:
            return result

    return None


def recommend_box_for_order(order_or_id: Union[Order, int, str]) -> Dict[str, Any]:
    """
    Recommends the most suitable box for an order.

    Algorithm Steps:
    1. Retrieve order and all associated products and quantities.
    2. Calculate total weight accurately using Decimal arithmetic.
    3. Validate box dimensions and max weight before evaluating each candidate.
    4. Filter and sort candidate boxes: Smallest Volume first, Lowest Cost as tie-breaker.
    5. Check weight capacity: Total Weight <= Box Maximum Weight.
    6. Simulate 3D physical placement testing all 6 orientations without overlap.
    7. Return the selected box or a clear descriptive message if none fit.
    """
    # 1. Resolve order instance
    if isinstance(order_or_id, Order):
        order = order_or_id
    elif isinstance(order_or_id, (int, str)):
        try:
            if isinstance(order_or_id, int) or str(order_or_id).isdigit():
                order = Order.objects.prefetch_related('items__product').get(id=int(order_or_id))
            else:
                order = Order.objects.prefetch_related('items__product').get(order_number=str(order_or_id))
        except Order.DoesNotExist:
            return {
                'success': False,
                'box': None,
                'order': None,
                'total_weight': Decimal('0.00'),
                'total_volume': Decimal('0.00'),
                'items_count': 0,
                'placements': [],
                'message': f"Order '{order_or_id}' was not found in the system."
            }
    else:
        return {
            'success': False,
            'box': None,
            'order': None,
            'total_weight': Decimal('0.00'),
            'total_volume': Decimal('0.00'),
            'items_count': 0,
            'placements': [],
            'message': "Invalid order identifier provided."
        }

    order_items = list(order.items.select_related('product').all())

    # Error handling: Empty order
    if not order_items:
        return {
            'success': False,
            'box': None,
            'order': order,
            'total_weight': Decimal('0.00'),
            'total_volume': Decimal('0.00'),
            'items_count': 0,
            'placements': [],
            'message': f"Order #{order.order_number} has no products to pack."
        }

    # 2. Expand products by quantity and compute total weight and volume
    expanded_items: List[Dict[str, Any]] = []
    total_weight = Decimal('0.00')
    total_volume = Decimal('0.00')

    for oi in order_items:
        prod = oi.product
        # Validate product dimensions and weight
        if prod.length <= 0 or prod.width <= 0 or prod.height <= 0 or prod.weight <= 0:
            return {
                'success': False,
                'box': None,
                'order': order,
                'total_weight': Decimal('0.00'),
                'total_volume': Decimal('0.00'),
                'items_count': 0,
                'placements': [],
                'message': f"Product '{prod.name}' has invalid non-positive dimensions or weight."
            }

        unit_vol = prod.length * prod.width * prod.height
        total_weight += prod.weight * oi.quantity
        total_volume += unit_vol * oi.quantity

        for _ in range(oi.quantity):
            expanded_items.append({
                'product_id': prod.id,
                'product_name': prod.name,
                'original_dims': (float(prod.length), float(prod.width), float(prod.height)),
                'volume': float(unit_vol),
                'weight': float(prod.weight),
            })

    # 3. Retrieve and validate all boxes
    all_boxes = list(Box.objects.all())
    if not all_boxes:
        return {
            'success': False,
            'box': None,
            'order': order,
            'total_weight': total_weight,
            'total_volume': total_volume,
            'items_count': len(expanded_items),
            'placements': [],
            'message': "No boxes are configured in the system."
        }

    rejection_reasons: List[str] = []
    boxes_with_metrics: List[Tuple[Decimal, Decimal, Box]] = []

    # Validate each box's dimensions and maximum weight capacity before evaluation
    for b in all_boxes:
        if b.length <= 0 or b.width <= 0 or b.height <= 0 or b.max_weight <= 0:
            rejection_reasons.append(
                f"{b.name}: Skipped due to invalid non-positive dimensions or max weight"
            )
            continue

        vol = b.length * b.width * b.height
        boxes_with_metrics.append((vol, b.cost, b))

    if not boxes_with_metrics:
        return {
            'success': False,
            'box': None,
            'order': order,
            'total_weight': total_weight,
            'total_volume': total_volume,
            'items_count': len(expanded_items),
            'placements': [],
            'message': "All configured boxes have invalid dimensions or weight capacities."
        }

    # Sort boxes: Smallest volume first, lowest cost as tie-breaker
    boxes_with_metrics.sort(key=lambda x: (x[0], x[1]))

    # 4. Evaluate valid boxes in ranked order
    for vol, cost, box in boxes_with_metrics:
        # Check weight capacity accurately
        if total_weight > box.max_weight:
            rejection_reasons.append(
                f"{box.name}: Exceeds weight capacity ({total_weight} kg > {box.max_weight} kg)"
            )
            continue

        # Simulate 3D placement (boundary check & non-overlap check across 6 orientations)
        placement_result = can_fit_in_box(expanded_items, box)
        if placement_result is not None:
            # Smallest suitable box found
            return {
                'success': True,
                'box': box,
                'order': order,
                'total_weight': total_weight,
                'total_volume': total_volume,
                'items_count': len(expanded_items),
                'placements': placement_result,
                'message': (
                    f"Selected box '{box.name}' "
                    f"(Dimensions: {box.length}x{box.width}x{box.height} cm, "
                    f"Volume: {vol:.2f} cm3, Cost: INR {box.cost:.2f})."
                )
            }
        else:
            rejection_reasons.append(
                f"{box.name}: Products do not physically fit inside boundaries"
            )

    # 5. If no box fits, construct clear explanation
    summary_reasons = "; ".join(rejection_reasons[:3])
    if len(rejection_reasons) > 3:
        summary_reasons += f" (+{len(rejection_reasons) - 3} more)"

    return {
        'success': False,
        'box': None,
        'order': order,
        'total_weight': total_weight,
        'total_volume': total_volume,
        'items_count': len(expanded_items),
        'placements': [],
        'message': (
            f"No available box can accommodate Order #{order.order_number} "
            f"(Total Weight: {total_weight} kg, Total Volume: {total_volume:.2f} cm3). "
            f"Evaluated {len(all_boxes)} boxes: {summary_reasons}."
        )
    }
