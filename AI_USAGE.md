# AI Usage Disclosure – PackWise Project

This document provides an honest and transparent summary of how artificial intelligence tools were used during the development of the PackWise Django application.

---

## 1. AI Tools Used

- **ChatGPT**: Used for initial project planning, understanding Django conventions, conceptual guidance on 3D packing algorithms, and general troubleshooting.
- **Antigravity**: Used as an AI coding assistant within the development environment to assist with implementing features, writing boilerplate code, refining templates and CSS, and generating unit tests.

---

## 2. How AI Assisted

AI tools were consulted across several stages of the project:

- **Django Project Setup**: Guidance on modular project organization into `products`, `boxes`, and `orders` applications, along with static file and template configurations.
- **Models and Database Structure**: Formulating model fields, relationships (`ForeignKey`, `CASCADE`, `PROTECT`), and positive value validation using Django's `MinValueValidator`.
- **3D Box-Packing Recommendation Logic**: Formulating the heuristic algorithm in `orders/services.py`, including 6-degree orientation calculations, 3D coordinate-based bounding box overlap detection, weight capacity checking, and volume/cost ranking.
- **Views, Templates, and CSS**: Implementing class/function-based views, Django forms (`ModelForm`), responsive HTML templates, and a clean custom CSS theme (navy blue, white, and teal).
- **Debugging and Testing Guidance**: Generating unit tests across models, forms, web views, and algorithm edge cases, as well as debugging runtime errors.

---

## 3. Prompts Given

Prompts provided during development focused on specific development milestones:
- High-level architectural prompts asking for project structure and app separation.
- Technical prompts requesting Django model definitions with strict validation for positive dimensions and weights.
- Algorithmic prompts describing the physical constraints of 3D item placement (non-overlapping boxes, orientation testing, weight limits).
- Frontend prompts specifying UI layout, navigation bar structure, and visual appearance.
- Testing prompts requesting test suites to verify valid packing, rotations, weight rejections, and form validations.

---

## 4. Outputs Accepted

AI-generated suggestions were reviewed before being integrated into the project:
- **Model Definitions**: Field definitions and validators for `Product`, `Box`, `Order`, and `OrderItem` models.
- **Form Handling**: Django `ModelForm` implementations and dynamic order item parsing logic.
- **Orientation Permutations**: The mathematical approach to rotating products across all 6 spatial orientations $(L, W, H)$.
- **Base UI Structure**: Responsive layout structure, navigation bar links, and CSS design tokens.
- **Test Structure**: Standard Django `TestCase` methods covering standard workflows and edge cases.

---

## 5. Outputs Modified or Rejected

Not all AI outputs were used as initially suggested. Several adjustments were required:
- **Dashboard Layout Revisions**: When AI added extra sections (such as counters, analytics grids, and workflow diagrams) that made the homepage cluttered, these were removed in favor of a clean, three-card layout matching the original design requirements.
- **Character Encoding Adjustments**: On Windows environments, AI-suggested special characters (such as the Indian Rupee symbol `₹` or multiplication symbols `×`) in string representations caused terminal encoding errors. Model string methods were adjusted to use ASCII-safe characters, while reserving proper symbols for HTML rendering.
- **Decimal Precision Adjustments**: Python floats suggested in test cases led to `DecimalField` validation errors. These were corrected to use `Decimal('0.00')` strings for exact decimal handling.
- **Card Sizing and Spacing**: Initial CSS styles generated disproportionate card heights; these were tuned to approximately 230–250px to ensure balanced visual hierarchy.

---

## 6. AI Mistakes and Limitations

Working with AI tools highlighted several common limitations:
- **Scope Creep / Over-Engineering**: AI sometimes generated unnecessary UI components or extra features beyond the required scope.
- **Platform-Specific Quirks**: AI occasionally overlooked Windows-specific quirks, such as console encoding limitations (`cp1252`).
- **Algorithm Limitations**: The implemented 3D packing algorithm in `orders/services.py` is a greedy heuristic using corner-point placement. It is designed to find a valid practical fit for common packing scenarios, but it is **not** a mathematically guaranteed optimal bin-packing solver. Complex packing combinations may exist that the heuristic does not discover.
- **No Native AI Integration**: Although the project name contains "AI-Assisted", the core application itself relies entirely on deterministic Python logic and geometric heuristics. No external machine learning APIs or LLMs are running inside the Django application.

---

## 7. Verification

All AI-suggested code was verified through testing and execution:
- **System Checks**: Verified using `python manage.py check` to ensure zero Django configuration issues.
- **Automated Tests**: An automated test suite of **32 tests** was executed via `python manage.py test`, confirming that product management, box management, order creation, rotational checking, weight constraints, and tie-breakers work as expected.
- **Manual Web Verification**: The application was run locally using `python manage.py runserver` to confirm that forms, error validation messages, navigation links, and recommendation results render accurately in the browser.

