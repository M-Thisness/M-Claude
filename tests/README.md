# M-Claude Test Suite

Comprehensive test suite for conversation processing and security features.

## 📋 Test Files

- **test_redaction.py** - 35 tests for redaction patterns (API keys, emails, phone numbers, UUIDs, etc.)
- **test_conversion.py** - Tests for JSONL to Markdown conversion
- **test_journals.py** - Tests for daily journal generation

## 🚀 Running Tests

### Install Dependencies

```bash
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
# Run all tests with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=scripts --cov-report=html

# Run tests in parallel (faster)
pytest tests/ -n auto
```

### Run Specific Tests

```bash
# Run only redaction tests
pytest tests/test_redaction.py -v

# Run specific test class
pytest tests/test_redaction.py::TestPhoneRedaction -v

# Run specific test
pytest tests/test_redaction.py::TestPhoneRedaction::test_uuid_preservation -v
```

## 📊 Test Results

**Current Status:**
- Total Tests: 35
- Passing: 31 (89%)
- Coverage: ~30% (scripts directory)

**Known Issues:**
- 4 tests need minor adjustments for pattern precedence
- Generic patterns sometimes match before specific patterns

## 🔍 Test Categories

### Redaction Tests (test_redaction.py)

#### API Key Redaction
- OpenAI API keys
- GitHub tokens
- Slack tokens
- AWS access keys

#### PII Redaction
- Email addresses
- Phone numbers (with UUID preservation)
- Credit card numbers
- SSN patterns

#### Security Redaction
- Private keys (RSA, generic)
- JWT tokens
- Database connection strings
- IP addresses

#### File Path Redaction
- Linux paths (`/home/user`)
- macOS paths (`/Users/user`)
- Windows paths (`C:\Users\user`)

#### Edge Cases
- Non-string inputs
- Empty content
- Multiple secrets in one message
- Real-world conversation scenarios

### Conversion Tests (test_conversion.py)

- Timestamp parsing and formatting
- Message formatting (user, assistant, tools)
- Markdown generation
- Code block preservation
- Link preservation

### Journal Tests (test_journals.py)

- Session summarization
- Time-of-day classification
- Date grouping
- File tracking
- Unicode handling

## 🛠️ Development

### Adding New Tests

```python
# tests/test_redaction.py
class TestNewFeature:
    """Test description"""

    def test_specific_case(self):
        text = "test input"
        result = redact_text(text)
        assert "expected" in result
```

### Test Fixtures

Common fixtures are in `tests/conftest.py`:
- Automatic path setup for importing scripts
- Shared test data (if needed)

## 🔧 Code Quality

### Format Code
```bash
black tests/
```

### Lint Code
```bash
flake8 tests/ --max-line-length=120
```

### Type Check
```bash
mypy tests/ --ignore-missing-imports
```

## 📝 CI/CD

Tests run automatically on:
- Pull requests to `main`
- Manual workflow dispatch

**Platforms tested:**
- Ubuntu (latest)
- Windows (latest)
- macOS (latest)

**Python versions:**
- 3.10
- 3.11
- 3.12

## ⚠️ Important Notes

### Test Data
- Use `TEST` or `EXAMPLE` prefixes for API keys
- Use intentionally invalid formats for tokens
- Avoid realistic-looking secrets (GitHub secret scanning will block)

**Good:**
```python
text = "api_key: sk_test_EXAMPLE1234567890"
text = "token: xoxb-TEST-EXAMPLE"
```

**Bad (will trigger secret scanning):**
```python
# DON'T use realistic-looking patterns like:
# "api_key: sk-" + "1234567890abcdefghijklmnop"
# "token: xoxb-" + "1234567890-abcdefghijklmnop"
```

## 📚 Coverage Reports

After running tests with coverage:

```bash
# View HTML report
open htmlcov/index.html  # macOS
start htmlcov/index.html # Windows
xdg-open htmlcov/index.html # Linux
```

## 🎯 Test Goals

- ✅ Verify redaction patterns work correctly
- ✅ Ensure UUIDs are not redacted as phone numbers
- ✅ Validate JSONL parsing
- ✅ Test cross-platform compatibility
- ✅ Maintain code quality standards

---

*For more information, see [IMPROVEMENTS.md](../IMPROVEMENTS.md)*
