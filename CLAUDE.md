# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

**pyhees-jjj** is a Python implementation of Japanese Building Energy Conservation Standard (BECC) energy consumption performance calculations for residential buildings. It's a fork/experimental variant of the original [pyhees](https://github.com/BRI-EES-House/pyhees) project, maintained by the Energy Conservation Performance Evaluation Method Study Committee within IBEC (Institute for Building Environment and Energy Conservation) and JSBC (Japan Sustainable Building Council).

The original calculation methodology is published by the Building Research Institute (BRI): https://www.kenken.go.jp/becc/house.html

## Common Development Commands

### Environment Setup
```bash
# Install dependencies with Poetry
poetry install

# Activate virtual environment
poetry shell
```

### Running Tests
```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest src/tests/test_denchu_01_unit.py

# Run tests in a specific directory
poetry run pytest src/tests/underfloor_ac/

# Run with verbose output
poetry run pytest -v

# Run specific test by name pattern
poetry run pytest -k "test_denchu"
```

### Running Calculations
```bash
# Run sample calculation (from repository root)
poetry run python sample.py

# Run custom experimental calculation
poetry run python -m jjjexperiment.main
```

### Code Quality
```bash
# Format code (if configured)
poetry run black src/

# Type checking (if configured)
poetry run mypy src/
```

### Key Distinction: pyhees vs pyhees-jjj

- **pyhees** (`src/pyhees/`): The base library containing core calculation modules for Japanese building energy standards
- **pyhees-jjj** (`src/jjjexperiment/`): An experimental fork with enhanced/modified logic for specific features:
  - Underfloor air conditioning (床下空調)
  - Carryover heat calculations (過剰熱量繰越)
  - Latent load handling (潜熱負荷)
  - Advanced denchu (電中研) models for room air conditioner (RAC) behavior

## High-Level Architecture

```
Input (JSON spec) 
    ↓
section2_2.calc_E_T() [Main orchestration - src/pyhees or jjjexperiment]
    ↓
    ├─ Section 3: Load Calculations (暖冷房負荷)
    ├─ Section 4: HVAC Equipment (暖冷房設備)
    ├─ Section 5: Ventilation (換気設備)
    ├─ Section 6: Lighting (照明設備)
    ├─ Section 7: Hot Water (給湯設備)
    ├─ Section 8: Cogeneration (コージェネレーション)
    ├─ Section 9: Photovoltaic (太陽光発電)
    └─ Section 10: Auxiliary (補助的な設備)
    ↓
Output: Annual primary energy consumption (MJ/year)
```

## Computational Module Structure

### Core Modules in `src/pyhees/`

The codebase is organized by **sections** corresponding to Japanese energy evaluation standards. Main calculation modules:

#### Section 2: Annual Primary Energy Consumption (第二章)
- **section2_1.py**: Environmental performance factor calculation
- **section2_2.py**: **Main entry point** - `calc_E_T(spec)` aggregates all equipment energy
- **section2_3.py**: Standard values and reference consumption

#### Section 3: Heating/Cooling Loads (第三章)
- **section3_1.py**: Load calculation with climate data
  - `calc_L_H_d_t_i()`: Hourly heating loads [MJ/h] for each zone
  - `calc_L_CS_d_t_i()`: Hourly sensible cooling loads
  - `calc_L_CL_d_t_i()`: Hourly latent cooling loads
- **section3_2.py**: Building envelope performance
  - Heat loss coefficient (Q), solar gain coefficient (μ)
- **section3_3.py**: Room thermal characteristics
- **section3_4.py**: Envelope component U-values (windows, doors, walls, etc.)
- **section3_5.py**: Solar radiation calculations

#### Section 4: HVAC Equipment (第四章) - Most Complex
- **section4_1.py**: Common HVAC functions
  - `calc_heating_load()`: Heating load calculation
  - `calc_cooling_load()`: Cooling load calculation
- **section4_2.py**: Ducted central air (ダクト式セントラル空調)
  - Large file (~200KB) with detailed air handling unit calculations
- **section4_2_a.py**: Duct-based equipment efficiency
- **section4_3.py**: Room air conditioner (RAC/ルームエアコン)
- **section4_4-4_10.py**: Other heating methods (FF heaters, electric heaters, floor heating, radiators, etc.)

#### Section 5: Ventilation (第五章)
- **section5.py**: `calc_E_E_V_d_t()` - Mechanical ventilation power consumption [kWh/h]

#### Section 6: Lighting (第六章)
- **section6.py**: `calc_E_E_L_d_t()` - Lighting power consumption

#### Section 7: Hot Water (第七章) - Complex Branching
- **section7_1.py**: Hot water load calculation
- **section7_2-7_6**: Different hot water equipment types (gas, electric, heat pump, etc.)

#### Section 8: Cogeneration (第八章)
- **section8.py**: CHP equipment (コージェネレーション)

#### Section 9: Photovoltaic (第九章)
- **section9_1-9_3.py**: PV generation and self-consumption

#### Section 10: Auxiliary Equipment (第十章)
- **section10.py**: Air purifiers, climate control (照度制御、空気清浄機)

#### Section 11: Common Functions (第十一章)
- **section11_1.py**: Climate data loading, common utilities
- **section11_3.py**: Occupancy schedules

### Key Data Files in `src/pyhees/data/`

- **climate/**: Regional weather data (AMeDAS-based, 8 regions)
  - Temperature, humidity, solar radiation for each hour of the year
- **solar/**: Solar radiation calculation tables
- **3-1_HukaData_151019_unifyLDK/**: Pre-calculated load profiles
  - Used when detailed load calculation isn't performed
- **outdoor.csv**: Outdoor air conditions table
- **schedule.csv**: Occupancy and equipment usage schedules

## The jjjexperiment Fork Structure

`src/jjjexperiment/` is a parallel codebase with experimental features. Key organization:

### Specialized Modules

1. **underfloor_ac/** (床下空調 - Underfloor Air Conditioning)
   - Experimental floor-based cooling/heating logic
   - Overrides section 4_2 (ducted AC) calculations
   - Files:
     - `section4_2.py`: Modified AC calculation
     - `section4_2_f40.py`, `section4_2_f46_f48.py`, `section4_2_f52.py`: Equipment-specific variants
     - `section3_1_e.py`: Load calculation for underfloor distribution

2. **carryover_heat/** (過剰熱量繰越 - Excess Heat Carryover)
   - Handles thermal mass effects and excess cooling/heating
   - File: `section4_2.py` with specialized temperature carry-forward logic
   - Includes: `get_C.py` for thermal capacitance calculations

3. **Main Application Code**
   - **main.py**: Orchestrates the entire calculation pipeline
     - Input parsing
     - Calls to core calculation sections
     - Handles both standard pyhees and custom logic
   - **input.py**: Input specification parsing and validation
   - **denchu_1.py**: DENCHU model (電中研モデル) for room air conditioner simulation
     - Detailed thermodynamic modeling: evaporator, condenser, compressor
     - Classes: `Spec`, `Condition` for equipment parameters
     - Functions for absolute humidity, bypass factor calculations
   - **denchu_2.py**: Secondary DENCHU model functions
   - **app_config.py**: Application configuration and constants
   - **constants.py**: Process type definitions and global constants
   - **di_container.py**: Dependency injection container setup
   - **inputs/**: Entity models for typed input parsing (Pydantic)
   - **ac_min_volume_input/**: Minimum air volume calculation logic

### Logic Composition Pattern

The jjjexperiment modules follow a **layering** approach:

```
pyhees base calculation (e.g., section4_2.calc_E_E_AC_d_t)
    ↓ (override via jjjexperiment)
Custom logic (denchu models, underfloor considerations)
    ↓
Final energy consumption result
```

Functions from `jjjexperiment.main` import both pyhees modules AND their own overrides, switching based on input parameters (e.g., `underfloor_air_conditioning_air_supply` flag).

## Input/Output Format

### Input Specification (Dictionary/JSON)

Building specification dict passed to `calc_E_T()`:

```python
spec = {
    # Basic info
    "region": 6,                          # Climate zone (1-8)
    "type": "一般住宅",                   # House type
    "tatekata": "戸建住宅",               # Construction type
    "A_A": 120.08,                        # Total floor area [m2]
    "A_MR": 29.81,                        # Main room area [m2]
    "A_OR": 51.34,                        # Other room area [m2]
    
    # Envelope (ENV)
    "ENV": {
        "method": "当該住宅の外皮面積の合計を用いて評価する",
        "A_env": 307.51,                  # Total envelope area [m2]
        "U_A": 0.87,                      # Heat loss coefficient [W/m2K]
        "eta_A_H": 4.3,                   # Winter solar gain [W/m2/(W/m2)]
        "eta_A_C": 2.8                    # Summer solar gain [W/m2/(W/m2)]
    },
    
    # Heating (H_*)
    "mode_H": "居室のみを暖房する方式",
    "H_MR": {"type": "ルームエアコンディショナー", ...},
    "H_OR": {"type": "ルームエアコンディショナー", ...},
    
    # Cooling (C_*)
    "mode_C": "居室のみを冷房する方式",
    "C_MR": {"type": "ルームエアコンディショナー", ...},
    "C_OR": {"type": "ルームエアコンディショナー", ...},
    
    # Hot Water (HW)
    "HW": {
        "has_bath": True,
        "hw_type": "ガス従来型給湯機",
        "bath_function": "ふろ給湯機(追焚あり)",
        ...
    },
    
    # Ventilation (V)
    "V": {
        "type": "ダクト式第二種換気設備",
        "input": "評価しない",
        "N": 0.5                          # ACH (air changes/hour)
    },
    
    # Optional: Lighting, Solar, Photovoltaic
    "L": {...},
    "SHC": None,
    "PV": None,
    ...
}
```

### Output: Energy Consumption Results

`calc_E_T(spec)` returns a tuple of 4 dicts:

1. **DesignedPrimaryEnergyTotal**: Various compliance standards (GJ/year)
   - `E_T_gn_du`: Building Energy Conservation Standard
   - `E_T_indc_du`: Guidance standard
   - `E_T_enh_du`: Low-carbon measure standard
   - etc.

2. **DesignedPrimaryEnergyTotalDash**: Excluding some contributions

3. **DesignedPrimaryEnergyDetail**: Component breakdown (MJ/year)
   ```python
   {
       "E_H": 45000,        # Heating
       "E_C": 28000,        # Cooling
       "E_V": 12000,        # Ventilation
       "E_L": 15000,        # Lighting
       "E_W": 35000,        # Hot water
       "E_S": -8000,        # Solar (negative = generation)
       "E_M": 5000,         # Miscellaneous
       ...
   }
   ```

4. **DesignedSecondaryEnergyDetail**: Secondary energy (electricity, gas, etc.)

## Calculation Patterns

### Time-Series Calculations

Most modules calculate hourly values for 365 days × 24 hours = 8,760 data points:

```python
# Typical function signature
def calc_something_d_t(region, ...) -> np.ndarray:
    """
    Returns: ndarray of shape (8760,) or (N_zones, 8760)
    Index mapping: d_t[hour] where hour = day*24 + hour_of_day
    """
```

### Load Calculation Flow

1. **Environmental inputs** (U_A, η values) → Section 3_2
2. **Climate data** (temperature, solar) + building parameters → Section 3_1
3. **Hourly loads** L_H_d_t_i, L_CS_d_t_i, L_CL_d_t_i
4. **HVAC equipment response** → Sections 4_1 through 4_10
5. **Energy consumption** (kWh, MJ) aggregation

### Equipment-Specific Overrides

For ducted AC (section 4_2), the calculation chain:
- pyhees: General ductwork and efficiency models
- jjjexperiment: Adds support for:
  - Underfloor distribution (thermal stratification)
  - Carryover from excess cooling (thermal storage)
  - DENCHU model for compressor part-load behavior

## Test Structure (`src/tests/`)

Tests are organized by feature and calculation area:

```
tests/
├── origin/              # Original/baseline tests
├── carryover_heat/      # Excess heat carryover tests
│   ├── test_4_2_formula_8_9.py
│   └── test_4_2_formula_46_48.py
├── latent_load/         # Latent cooling load tests
│   ├── test_4_2_formula_35_36.py
│   └── test_4_2_a_formula_35_36.py
├── underfloor_ac/       # Underfloor AC tests
│   ├── test_4_2.py
│   ├── test_4_2_f40.py
│   ├── test_4_2_f46_f48.py
│   └── test_4_2_f52.py
├── inputs/              # Input parsing tests
├── test_denchu_01_unit.py    # DENCHU model unit tests
├── test_denchu_02_modeling.py # DENCHU model validation
└── test_not_broken_*.py      # Regression tests
```

Tests use pytest and follow Arrange-Act-Assert pattern with numpy array comparisons.

## Key Architectural Insights

### 1. Modular Section-Based Design
- Each "section" (3, 4, 5, 6, 7, 8, 9, 10, 11) maps to Japanese building standards
- Sections are relatively independent but share utility functions
- Makes it easy to locate calculation logic for a specific building system

### 2. Hourly Time-Series as Central Pattern
- All calculations maintain hourly resolution (8,760 hours/year)
- Allows for accurate load matching and equipment response
- Results aggregated to annual totals for compliance

### 3. Separation of Concerns
- **Loads** (Section 3): Purely thermodynamic, no equipment efficiency
- **Equipment** (Sections 4-10): Convert loads to energy consumption
- **Compliance** (Section 2): Aggregate per building standard

### 4. Custom Logic via Parallel Modules
- jjjexperiment doesn't replace pyhees, it sits alongside
- main.py acts as router: use pyhees standard OR jjjexperiment custom
- Enables experimentation without breaking base library

### 5. Dependency Injection
- `di_container.py` provides AppConfig via Injector
- Allows runtime configuration of behavior (e.g., underfloor AC flag)
- Constants updated from input: `jjj_consts.set_constants(input_data)`

## Common Entry Points

### For Standard Calculation
```python
from pyhees.section2_2 import calc_E_T
results = calc_E_T(spec_dict)
```

### For Custom Experimental Logic
```python
from jjjexperiment.main import calc
results = calc(input_data, test_mode=False)
```

### For Component Testing
```python
from pyhees.section4_2 import calc_E_E_AC_d_t  # Individual module function
energy = calc_E_E_AC_d_t(...)
```

## Dependencies

- **numpy**: Array operations for hourly calculations
- **pandas**: Data loading and time-series handling
- **scipy**: Scientific computing for heat transfer models
- **pydantic**: Input validation (v2.10.6+)
- **pyyaml**: Configuration files
- **injector**: Dependency injection

All at Python 3.12.11+

## Summary for Future Claude Instances

When working on this codebase:

1. **Start at section2_2.py** for the main calculation flow
2. **Understand the input spec structure** before diving into implementations
3. **Recognize the jjjexperiment overlay**: It's experimental enhancement, not replacement
4. **Time-series indexing**: d_t arrays are always [0..8759] for hours of the year
5. **Equipment branching**: Section 4 has extensive if/elif logic based on equipment type
6. **Tests validate against official standards**: See reference PDF links in code comments
7. **Climate regions (1-8) are hardcoded**: Different regions have different load profiles
8. **The DENCHU model is physics-based**: For RAC equipment, not a lookup table

