# Django Repository Test Queries

## Repository Information

**Repository:** Django Web Framework
**Path:** `D:/code/bench/django-repo`
**Total Commits Analyzed:** 100
**Test Cases Generated:** 49
**Repository Size:** ~551K commits, 6,990 files
**Language:** Python (web framework)

## Why Django?

Django is perfect for benchmarking because:
- ✅ Large, mature codebase with real production code
- ✅ Clear, descriptive commit messages
- ✅ Actual bug fixes and feature implementations
- ✅ Well-structured with models, views, forms, migrations, etc.
- ✅ Mix of core code and tests

## Test Queries (First 20)

### Query 1
**Query:** `Fixed -- Extended fields.E004 system check for unordered iterables.`
**Expected Files (3):**
- `django/db/models/fields/__init__.py`
- `docs/ref/checks.txt`
- `tests/invalid_models_tests/test_ordinary_fields.py`
**Type:** Bug fix in model fields validation

---

### Query 2
**Query:** `Fixed -- Escaped attributes in Stylesheet.__str__ .`
**Expected Files (4):**
- `django/utils/feedgenerator.py`
- `docs/releases/5.2.9.txt`
- `tests/syndication_tests/tests.py`
- `tests/utils_tests/test_feedgenerator.py`
**Type:** Security fix in feed generation

---

### Query 3
**Query:** `Fixed -- Checked for applied replaced migrations recursively.`
**Expected Files (3):**
- `django/db/migrations/executor.py`
- `django/db/migrations/loader.py`
- `tests/migrations/test_commands.py`
**Type:** Bug fix in database migrations

---

### Query 4
**Query:** `Refs -- Added introspection support for PostgreSQL HStoreField.`
**Expected Files (6):**
- `django/contrib/postgres/apps.py`
- `django/db/backends/postgresql/base.py`
- `django/db/backends/postgresql/introspection.py`
- `docs/releases/6.1.txt`
- `tests/backends/postgresql/tests.py`
- `tests/postgres_tests/test_introspection.py`
**Type:** Feature addition for PostgreSQL

---

### Query 5
**Query:** `Fixed -- Removed invalid for attribute on legend tags.`
**Expected Files (7):**
- `django/forms/boundfield.py`
- `tests/forms_tests/tests/test_forms.py`
- `tests/forms_tests/tests/test_i18n.py`
- `tests/forms_tests/widget_tests/test_clearablefileinput.py`
- `tests/forms_tests/widget_tests/test_selectdatewidget.py`
- `tests/model_forms/tests.py`
- `tests/model_formsets/tests.py`
**Type:** HTML/Forms bug fix

---

### Query 6
**Query:** `Fixed -- Defaulted to running checks against all databases.`
**Expected Files (2):**
- `django/core/checks/registry.py`
- `tests/check_framework/tests.py`
**Type:** System checks improvement

---

### Query 7
**Query:** `Refs -- Adjusted passing of Field.check kwargs to ArrayField.base field.`
**Expected Files (2):**
- `django/contrib/postgres/fields/array.py`
- `tests/postgres_tests/test_array.py`
**Type:** PostgreSQL array field fix

---

### Query 8
**Query:** `Refs -- Augmented regression tests for database system checks.`
**Expected Files (2):**
- `tests/check_framework/tests.py`
- `tests/migrations/test_commands.py`
**Type:** Test improvement

---

### Query 9
**Query:** `Fixed -- Fixed constraint validation crash for excluded FK attnames.`
**Expected Files (3):**
- `django/db/models/base.py`
- `tests/constraints/tests.py`
- `tests/invalid_models_tests/test_models.py`
**Type:** Database constraint bug fix

---

### Query 10
**Query:** `Fixed -- Redirect authenticated users on admin login view to next URL.`
**Expected Files (5):**
- `django/contrib/admin/sites.py`
- `docs/releases/5.2.9.txt`
- `tests/admin_views/test_adminsite.py`
- `tests/admin_views/tests.py`
- `tests/admin_views/urls.py`
**Type:** Admin interface improvement

---

### Query 11
**Query:** `Refs -- Made JSONNull deconstruct using convenient import path.`
**Expected Files (2):**
- `django/contrib/postgres/fields/jsonb.py`
- `tests/postgres_tests/test_json.py`
**Type:** JSON field improvement

---

### Query 12
**Query:** `Refs -- Ran further selenium tests with --parallel 1.`
**Expected Files (2):**
- `tests/admin_inlines/tests.py`
- `tests/admin_views/tests.py`
**Type:** Test configuration

---

### Query 13
**Query:** `Fixed -- Fixed placement of FilteredSelectMultiple widget label.`
**Expected Files (2):**
- `django/contrib/admin/static/admin/css/widgets.css`
- `tests/admin_widgets/tests.py`
**Type:** Admin widget CSS fix

---

### Query 14
**Query:** `Fixed -- Handled non-finite Decimals in intcomma filter.`
**Expected Files (2):**
- `django/contrib/humanize/templatetags/humanize.py`
- `tests/humanize_tests/tests.py`
**Type:** Template filter bug fix

---

### Query 15
**Query:** `Fixed -- Used actual SQLite limits in last executed query quoting.`
**Expected Files (2):**
- `django/db/backends/sqlite3/operations.py`
- `tests/backends/sqlite/tests.py`
**Type:** SQLite backend fix

---

### Query 16
**Query:** `Fixed -- Allowed overriding CSRF_COOKIE_HTTPONLY in tests.`
**Expected Files (2):**
- `django/test/utils.py`
- `tests/csrf_tests/tests.py`
**Type:** Testing utility improvement

---

### Query 17
**Query:** `Fixed -- Allowed overriding CSRF_COOKIE_SAMESITE in tests.`
**Expected Files (2):**
- `django/test/utils.py`
- `tests/csrf_tests/tests.py`
**Type:** Testing utility improvement

---

### Query 18
**Query:** `Fixed -- Allowed overriding CSRF_COOKIE_SECURE in tests.`
**Expected Files (2):**
- `django/test/utils.py`
- `tests/csrf_tests/tests.py`
**Type:** Testing utility improvement

---

### Query 19
**Query:** `Fixed -- Allowed overriding CSRF_COOKIE_DOMAIN in tests.`
**Expected Files (2):**
- `django/test/utils.py`
- `tests/csrf_tests/tests.py`
**Type:** Testing utility improvement

---

### Query 20
**Query:** `Fixed -- Allowed overriding CSRF_COOKIE_PATH in tests.`
**Expected Files (2):**
- `django/test/utils.py`
- `tests/csrf_tests/tests.py`
**Type:** Testing utility improvement

---

## Query Categories

The Django test set includes diverse query types:

### Bug Fixes (Most Common)
- Model field validation
- Migration handling
- Form rendering
- Database operations
- Security issues

### Feature Additions
- PostgreSQL HStore support
- Database introspection
- Admin improvements

### Test Improvements
- Selenium test configuration
- Regression tests
- Test utilities

### Code Quality
- CSS fixes
- Template filters
- Backend operations

## Comparison with Requests Repository

| Aspect | Requests Repo | Django Repo |
|--------|---------------|-------------|
| **Test Cases** | 11 | 49 |
| **Query Types** | Mostly version bumps | Actual code changes |
| **File Types** | Workflows, configs | Python code, tests, docs |
| **Complexity** | Simple (2-4 files) | Varied (2-7 files) |
| **Code Focus** | Infrastructure | Application logic |

## Testing with Greb MCP

### Sample Prompt Format

For each query, use this format in Kiro:

```
Use Greb to search in D:/code/bench/django-repo for: "Fixed -- Extended fields.E004 system check for unordered iterables."
```

### Expected Better Results

Django queries should work better with Greb because:
1. **Semantic meaning** - Queries describe actual code changes
2. **Code context** - Real Python files with clear purposes
3. **Descriptive names** - Files like `fields/__init__.py`, `migrations/executor.py`
4. **Test correlation** - Tests often match the code being changed

## Running the Evaluation

### Quick Test (First 10 queries)
```bash
# Create a smaller gold set
python -c "import json; data = json.load(open('django_gold_set.json')); data['test_cases'] = data['test_cases'][:10]; json.dump(data, open('django_gold_set_small.json', 'w'), indent=2)"

# Run evaluation
python examples/evaluate_copilot_greb.py
# (Update script to use django_gold_set_small.json and django-repo)
```

### Full Evaluation (All 49 queries)
```bash
python examples/evaluate_copilot_greb.py
# (Update script to use django_gold_set.json and django-repo)
```

### Automated (if Greb has CLI/API)
```bash
python examples/evaluate_greb_automated.py
# (Update configuration for Django repo)
```

## Expected Performance

### Baseline (Keyword Search)
- F1 Score: ~0.10-0.15 (based on Requests results)
- Many false positives

### Greb (Expected)
- F1 Score: Should be **much higher** (0.30-0.60+)
- Better semantic understanding
- Fewer false positives
- Should understand code structure

## Next Steps

1. **Test a few queries manually** in Kiro with Greb
2. **Compare results** with expected files
3. **Run full evaluation** if results look promising
4. **Analyze patterns** - which query types work best?

---

**Total Queries Available:** 49
**Repository:** Django (production-grade Python web framework)
**Ready for Testing:** ✅

See `django_gold_set.json` for complete list of all 49 test cases!
