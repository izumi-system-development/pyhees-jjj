# Test Code Preferences

## Test Framework
- **pytest Only**: Use pytest framework exclusively, never use unittest.TestCase
- **pytest Features**: Use pytest.mark.parametrize, pytest.approx, pytest fixtures

## Test Structure
- **AAA Pattern**: All tests must follow Arrange-Act-Assert structure with clear comments
- **Flexible AAA**: When it makes tests simpler, Arrange & Act can be combined into a single section
- **Japanese Comments**: Use Japanese for docstrings and comments for development team
- **Focused Tests**: One test per specific behavior, avoid complex integration tests

## Test Naming Convention
- **File Names**: `test_{subject}_f_{formula_numbers}.py`
- **Examples**: 
  - `test_fan_power_f_37_38.py` (formulas 37 & 38)
  - `test_heating_cooling_load_f_1_2.py` (formulas 1 & 2)
- **Class Names**: Use Japanese descriptive names (pure pytest classes)
  - `class ファン電力計算テスト:`
  - `class 暖冷房負荷計算テスト:`
- **Method Names**: Use Japanese descriptive names
  - `def test_基本計算_正常値(self):`
  - `def test_境界値_ゼロ負荷(self):`
  - `def test_異常値_負の値(self):`
- **Benefits**: Clear subject identification, formula number reference, searchable, Japanese team readability

## Test Organization
```
src/tests/{feature}/
├── test_{subject}_f_{nums}.py        # Unit tests for specific formulas
├── test_{subject}_f_{nums}.py
└── test_{feature}_integration.py     # Integration tests for feature
```

**Example:**
```
src/tests/latent_load/               # latent_load = 潜熱評価 feature
├── test_fan_power_f_37_38.py
├── test_heating_cooling_load_f_1_2.py
└── test_latent_load_integration.py
```

## Array Handling
- **Full Year Arrays**: Use `np.zeros(8760)` for functions expecting annual data
  - **8760 = 24 hours × 365 days** (hourly data for full year)
  - **Index 0**: January 1st, 1:00 AM (middle of winter) → Use for **Heating tests**
  - **Index 4848**: Summer period → Use for **Cooling tests**
- **Test Data Placement**: Set test values at seasonally appropriate indices
- **Proper Indexing**: Verify array bounds and expected lengths

## Test Content Guidelines
- **Japanese Names**: Use Japanese for class names, method names, docstrings, and comments
- **Minimal Setup**: Avoid complex preparation functions
- **Direct Assertions**: Test specific expected values, not just "something changed"
- **Edge Cases**: Include zero load, boundary conditions, parameter variations
- **Seasonal Testing**: Use appropriate indices for 暖房 (index 0) and 冷房 (index 4848)

## Anti-Patterns to Avoid
- Complex setup functions with 100+ lines
- Integration tests disguised as unit tests
- Weak assertions like `assert not np.array_equal()` without context
- Shared test state between methods
- Testing entire calculation workflows in unit tests

## Example AAA Structure

### Standard AAA Pattern
```python
class Testファン電力計算:
    """ファン電力計算のテストクラス"""

    def test_基本計算_正常値(self):
        """基本計算のテスト - 正常値"""
        # Arrange
        param1 = 100.0
        param2 = np.zeros(8760)
        param2[0] = 50.0  # 暖房期のインデックス

        # Act
        result = target_function(param1, param2)

        # Assert
        assert isinstance(result, np.ndarray)
        assert result[0] > 0
```

### Combined Arrange & Act (when simpler)
```python
class Test温度計算:
    """温度計算のテストクラス"""

    def test_基本計算_正常値(self):
        """基本計算のテスト - 正常値"""
        # Arrange & Act
        result = target_function(
            temperature=20.0,  # 設定温度
            load=5.17,        # 負荷
            area=51.34        # 面積
        )

        # Assert
        assert result == pytest.approx(19.39, abs=1e-2)
```

### Parametrized Tests
```python
class Test計算:
    """計算のテストクラス"""

    @pytest.mark.parametrize("input_data, expected", [
        ((10, 20), 30),
        ((5, 15), 20),
    ])
    def test_パラメータ化テスト(self, input_data, expected):
        """パラメータ化テスト"""
        # Arrange & Act
        result = target_function(*input_data)
        
        # Assert
        assert result == expected
```
