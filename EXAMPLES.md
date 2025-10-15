# ETIM MCP Server - Usage Examples

This guide demonstrates real-world usage scenarios and workflows for the ETIM MCP Server.

## Table of Contents

- [Quick Start Examples](#quick-start-examples)
- [Advanced Filtering (v1.2.0)](#advanced-filtering-v120)
- [Business Use Cases](#business-use-cases)
- [Multi-Step Workflows](#multi-step-workflows)
- [Batch Operations](#batch-operations)
- [Version Management](#version-management)

---

## Quick Start Examples

### Example 1: Basic Product Search

**Scenario**: Find cable products in the ETIM database.

**Natural Language Query**:
```
Search ETIM for cable products
```

**Tool Call**: `search_classes`
```json
{
  "search_text": "cable",
  "language": "EN",
  "max_results": 10
}
```

**Response**:
```json
{
  "total": 1599,
  "classes": [
    {
      "code": "EC001679",
      "version": 6,
      "status": 5,
      "mutationDate": "2022-05-26T07:16:06.467",
      "modelling": false
    }
  ],
  "search_text": "cable",
  "language": "EN"
}
```

**Result**: Found 1,599 cable-related classes across all ETIM versions.

---

### Example 2: Get Product Details

**Scenario**: Get detailed information about a specific charging device.

**Natural Language Query**:
```
Get details for ETIM class EC002883
```

**Tool Call**: `get_class_details`
```json
{
  "class_code": "EC002883",
  "language": "EN",
  "include_features": true
}
```

**Key Information Returned**:
- Description: "Charging device E-Mobility"
- 37 features including:
  - Number of charging points
  - Rated voltage
  - IP protection rating
  - Communication protocols (OCPP, etc.)
- Group: "EG000039" (Accessories for E-Mobility)
- Translations in 7 languages

---

### Example 3: Find Features

**Scenario**: Search for IP rating features.

**Natural Language Query**:
```
Search for IP protection rating features
```

**Tool Call**: `search_features`
```json
{
  "search_text": "IP",
  "language": "EN",
  "max_results": 10
}
```

**Response**: List of features like:
- EF000012: "Degree of protection (IP) First numeral"
- EF000013: "Degree of protection (IP) Second numeral"
- EF003033: "Degree of protection (IP)"

---

## Advanced Filtering (v1.2.0)

### Example 4: Filter by ETIM Release

**Scenario**: Find only products from ETIM 9.0 (exclude newer versions).

**Natural Language Query**:
```
Search for lamp products, but only show those from ETIM 9.0
```

**Tool Call**: `search_classes`
```json
{
  "search_text": "lamp",
  "language": "EN",
  "max_results": 10,
  "release_filter": ["ETIM-9.0"]
}
```

**Results**:
- Without filter: **1,368 classes**
- With ETIM-9.0 filter: **317 classes**
- **Reduction**: 77% (only ETIM-9.0 products)

**Use Case**: Testing against specific ETIM version, legacy system compatibility.

---

### Example 5: Filter by Product Group

**Scenario**: Find all classes in the "Cables" product group.

**Natural Language Query**:
```
Show me all products in the cable accessories group EG000017
```

**Tool Call**: `search_classes`
```json
{
  "search_text": "",
  "language": "EN",
  "max_results": 20,
  "group_filter": ["EG000017"]
}
```

**Result**: **425 classes** in the cable accessories group.

**Use Case**: Browse all products in a specific category, catalog generation.

---

### Example 6: Combine Multiple Filters

**Scenario**: Find products from DYNAMIC release in specific product groups.

**Natural Language Query**:
```
Find products in DYNAMIC from groups EG000017 and EG000020
```

**Tool Call**: `search_classes`
```json
{
  "search_text": "",
  "language": "EN",
  "max_results": 50,
  "release_filter": ["DYNAMIC"],
  "group_filter": ["EG000017", "EG000020"]
}
```

**Filtering Steps**:
1. All products: 21,538 classes
2. + DYNAMIC filter: 5,666 classes
3. + Group filter (2 groups): **42 precise matches**

**Use Case**: Precise product catalog filtering, migration planning.

---

### Example 7: Exclude BIM/Modelling Classes

**Scenario**: Get only standard product classes, exclude 3D modelling variants.

**Natural Language Query**:
```
Search for downlight products, but exclude modelling classes
```

**Tool Call**: `search_classes`
```json
{
  "search_text": "downlight",
  "language": "EN",
  "max_results": 10,
  "exclude_modelling": true
}
```

**Use Case**: E-commerce catalogs (don't need 3D models), standard product listings.

---

### Example 8: Find What's New in DYNAMIC

**Scenario**: Compare ETIM-10.0 vs DYNAMIC to find new products.

**Workflow**:

**Step 1**: Get ETIM-10.0 class count
```json
{
  "search_text": "",
  "max_results": 1,
  "release_filter": ["ETIM-10.0"]
}
```
**Result**: 5,640 classes

**Step 2**: Get DYNAMIC (current) class count
```json
{
  "search_text": "",
  "max_results": 1,
  "release_filter": ["DYNAMIC"]
}
```
**Result**: 5,666 classes

**Answer**: **26 new classes** added since ETIM-10.0

**Use Case**: Stay current with ETIM updates, plan database migrations.

---

## Business Use Cases

### Use Case 1: E-Commerce Product Catalog

**Scenario**: An online electrical product store needs to standardize their product data.

**Workflow**:

1. **Search for product category**:
   ```
   Search ETIM for LED downlight products
   ```

2. **Get detailed specifications**:
   ```
   Get details for ETIM class EC001744
   ```

3. **Extract key features for product pages**:
   - Power consumption (Watts)
   - Color temperature (Kelvin)
   - IP protection rating
   - Mounting type
   - Beam angle

4. **Get values for filter facets**:
   ```
   Search for color temperature values
   ```

**Result**: Standardized product attributes for consistent catalog data.

---

### Use Case 2: Product Data Migration

**Scenario**: Migrate legacy product database to ETIM standard.

**Workflow**:

1. **Identify target ETIM release**:
   ```
   Get ETIM releases
   ```
   Result: Choose ETIM-10.0 for stability

2. **Map products to ETIM classes**:
   ```
   Search for "miniature circuit breaker"
   ```
   Result: EC000034

3. **Get class details for version 10.0 specifically**:
   ```json
   {
     "class_code": "EC000034",
     "release": "ETIM-10.0",
     "include_features": true
   }
   ```

4. **Map legacy attributes to ETIM features**:
   - "Amp Rating" → Feature EF000123
   - "Pole Count" → Feature EF000456

5. **Validate data against ETIM values**:
   ```
   Get details for value EV010186
   ```

**Result**: Clean migration to ETIM-compliant product data.

---

### Use Case 3: Competitive Product Analysis

**Scenario**: Compare similar products from different manufacturers.

**Workflow**:

1. **Find comparable products**:
   ```
   Search for electric vehicle charging stations
   ```
   Result: EC002883, EC002884

2. **Compare classes side-by-side**:
   ```json
   {
     "class_codes": ["EC002883", "EC002884"],
     "language": "EN"
   }
   ```

3. **Analyze feature differences**:
   - Charging power capabilities
   - Number of charging points
   - Communication protocols
   - Mounting options

4. **Get value details for specific features**:
   ```
   Get details for value EV012345 (OCPP 2.0 support)
   ```

**Result**: Detailed competitive analysis matrix.

---

### Use Case 4: Technical Documentation Generation

**Scenario**: Generate specification sheets for products.

**Workflow**:

1. **Get complete class details**:
   ```json
   {
     "class_code": "EC002883",
     "version": 2,
     "language": "EN",
     "include_features": true
   }
   ```

2. **Organize features by groups**:
   ```
   Get details for feature group EFG00007 (Electrical)
   ```

3. **Include unit abbreviations**:
   ```
   Get details for unit EU570448 (millimeters)
   ```

4. **Generate multilingual docs**:
   - Repeat queries with `language: "de-DE"`
   - Repeat queries with `language: "fr-BE"`

**Result**: Professional, standardized technical documentation.

---

## Multi-Step Workflows

### Workflow 1: Product Classification Audit

**Goal**: Verify product classifications are current.

**Steps**:

1. **List all products in your catalog** (from your system)

2. **For each product, get current ETIM class**:
   ```
   Get details for class EC001744
   ```

3. **Check if class has been updated**:
   ```json
   {
     "class_code": "EC001744",
     "version": 6,
     "language": "EN"
   }
   ```

4. **Get change history**:
   ```json
   {
     "class_code": "EC001744",
     "version": 6
   }
   ```

5. **Review differences**:
   - New features added
   - Deprecated features
   - Changed descriptions

**Result**: Updated product classifications with change log.

---

### Workflow 2: Build Product Recommendation Engine

**Goal**: Find similar products based on features.

**Steps**:

1. **Get source product details**:
   ```json
   {
     "class_code": "EC001744",
     "include_features": true
   }
   ```

2. **Extract key features**:
   - Power consumption: 10W
   - Color temperature: 3000K
   - IP rating: IP65

3. **Search for products in same group**:
   ```json
   {
     "search_text": "downlight",
     "group_filter": ["EG000023"],
     "max_results": 50
   }
   ```

4. **Compare features**:
   ```json
   {
     "class_codes": ["EC001744", "EC001745", "EC001746"]
   }
   ```

5. **Rank by feature similarity**

**Result**: Ranked list of similar products for recommendations.

---

### Workflow 3: Market Analysis by Release

**Goal**: Analyze product evolution across ETIM versions.

**Steps**:

1. **Get all versions of a class**:
   ```json
   {
     "class_code": "EC002883",
     "include_features": false
   }
   ```
   Result: 5 versions found

2. **Get details for first and latest version**:
   ```json
   {
     "classes": [
       {"code": "EC002883", "version": 1},
       {"code": "EC002883", "version": 5}
     ],
     "include_features": true
   }
   ```

3. **Analyze feature changes**:
   - Version 1: 28 features
   - Version 5: 37 features
   - **9 new features** added

4. **Get specific version differences**:
   ```json
   {
     "class_code": "EC002883",
     "version": 5
   }
   ```

**Result**: Product evolution timeline with feature additions.

---

## Batch Operations

### Batch Example 1: Catalog Update

**Scenario**: Update 100 products in your catalog with latest ETIM data.

**Efficient Approach**:

```json
{
  "classes": [
    {"code": "EC001744"},
    {"code": "EC001679"},
    {"code": "EC002883"},
    // ... up to 100 classes
  ],
  "language": "EN",
  "include_features": true
}
```

**Benefits**:
- Single API call instead of 100
- Faster overall execution
- Lower API quota usage
- Better cache efficiency

---

### Batch Example 2: Version Comparison

**Scenario**: Compare versions 7, 8, 9, 10 of circuit breaker class.

**Request**:
```json
{
  "classes": [
    {"code": "EC000034", "version": 7},
    {"code": "EC000034", "version": 8},
    {"code": "EC000034", "version": 9},
    {"code": "EC000034", "version": 10}
  ],
  "language": "EN",
  "include_features": true
}
```

**Analysis**:
- Compare feature counts
- Identify added/removed features
- Track specification changes

---

## Version Management

### Version Example 1: Get Version History

**Scenario**: See how a product classification evolved.

**Tool Call**: `get_all_class_versions`
```json
{
  "class_code": "EC002883",
  "language": "EN",
  "include_features": false
}
```

**Response**: List of all versions (1, 2, 3, 4, 5) with:
- Mutation dates
- Revision numbers
- Status codes

**Use Case**: Understanding classification stability, planning migrations.

---

### Version Example 2: Compare Specific Versions

**Scenario**: See what changed between version 4 and 5.

**Tool Call**: `get_class_diff`
```json
{
  "class_code": "EC002883",
  "version": 5,
  "language": "EN"
}
```

**Response**: Class details WITH change indicators:
- 🆕 New features added in version 5
- ❌ Features removed since version 4
- 🔄 Modified feature descriptions
- ℹ️ Unchanged features

**Use Case**: Release notes, migration impact assessment.

---

### Version Example 3: Freeze to Specific Release

**Scenario**: Get class as it was in ETIM-9.0 (for legacy systems).

**Tool Call**: `get_class_for_release`
```json
{
  "class_code": "EC000034",
  "release": "ETIM-9.0",
  "language": "EN",
  "include_features": true
}
```

**Result**: Exact class definition from ETIM-9.0, even if newer versions exist.

**Use Case**: Legacy system compatibility, regression testing.

---

## Advanced Techniques

### Technique 1: Progressive Filtering

Start broad, then narrow down:

```
Step 1: Search all products
  → 21,538 classes

Step 2: Add search text "cable"
  → 1,599 classes

Step 3: Add release filter "ETIM-9.0"
  → 350 classes

Step 4: Add group filter ["EG000017", "EG000020"]
  → 42 classes

Step 5: Review results and get details
```

---

### Technique 2: Feature-Driven Search

Find products by specific features:

```
Step 1: Search features for "IP65"
  → Get feature code EF000012

Step 2: Search classes with that feature
  → feature_filter: ["EF000012"]
  → Products with IP65 rating

Step 3: Get value details for IP65
  → Understand exact specification
```

---

### Technique 3: Group Exploration

Navigate the ETIM hierarchy:

```
Step 1: Search for top-level group
  → "Lighting products"
  → EG000001

Step 2: Get group details with releases
  → See which ETIM versions include it

Step 3: Get all classes in group
  → group_filter: ["EG000001"]

Step 4: Get subgroups
  → Search groups with "downlight"
  → EG000023
```

---

## Tips & Best Practices

### 🎯 Performance Tips

1. **Use filtering** instead of fetching all results and filtering locally
2. **Cache aggressively** - repeated queries are 20x faster
3. **Batch operations** when getting multiple classes
4. **Exclude features** when you don't need them (`include_features: false`)

### 🔍 Search Tips

1. **Empty search text** to browse all products in a group
2. **Combine filters** for precise results
3. **Use language codes** for multilingual applications
4. **Filter by release** to maintain version consistency

### 📊 Data Management Tips

1. **Store ETIM codes** in your database, not full details
2. **Cache class details** locally for frequently accessed products
3. **Use version numbers** to track classification changes
4. **Batch update** products periodically from latest ETIM

### 🚀 Integration Tips

1. **Map your categories** to ETIM groups first
2. **Create lookup tables** for common values
3. **Validate data** against ETIM before import
4. **Use health checks** to monitor API availability

---

## Common Patterns

### Pattern 1: Product Search → Details → Compare

```
1. search_classes("cable")
   → Find relevant classes

2. get_class_details("EC001679")
   → Get full specifications

3. compare_classes(["EC001679", "EC001680"])
   → Side-by-side comparison
```

### Pattern 2: Group → Classes → Features

```
1. search_groups("lighting")
   → Find group EG000023

2. search_classes(group_filter=["EG000023"])
   → All products in group

3. get_class_details("EC001744")
   → Features for specific product
```

### Pattern 3: Release Comparison

```
1. search_classes(release_filter=["ETIM-9.0"])
   → Classes in version 9.0

2. search_classes(release_filter=["ETIM-10.0"])
   → Classes in version 10.0

3. Compare counts
   → Identify new products
```

---

## Troubleshooting Examples

### Issue: Too Many Results

**Problem**: Search returns 5,000+ classes

**Solution**: Add filters
```json
{
  "search_text": "light",
  "group_filter": ["EG000023"],  // Narrow to downlights
  "release_filter": ["ETIM-10.0"],  // Specific version
  "max_results": 50
}
```

---

### Issue: Missing Features

**Problem**: Class details don't show features

**Solution**: Ensure `include_features: true`
```json
{
  "class_code": "EC001744",
  "include_features": true  // Default is true, but be explicit
}
```

---

### Issue: Different Results in Different Languages

**Problem**: Class has different features in German vs English

**Solution**: This is expected - ETIM is multilingual
```json
{
  "class_code": "EC001744",
  "language": "de-DE"  // Get German version
}
```

Compare both versions to ensure consistency.

---

## Real Response Examples

### Small Response: Simple Search

**Request**:
```json
{
  "search_text": "cable",
  "max_results": 3
}
```

**Response** (~500 bytes):
```json
{
  "total": 1599,
  "classes": [
    {"code": "EC001679", "version": 6, "status": 5},
    {"code": "EC002870", "version": 1, "status": 5},
    {"code": "EC000536", "version": 4, "status": 5}
  ]
}
```

---

### Medium Response: Class Details

**Request**:
```json
{
  "class_code": "EC002883",
  "include_features": true
}
```

**Response** (~15KB):
- Full description in 7 languages
- 37 features with types, units, values
- Group information with translations
- Synonyms and keywords

---

### Large Response: Batch with Features

**Request**:
```json
{
  "classes": [
    {"code": "EC001744"},
    {"code": "EC001679"},
    {"code": "EC002883"}
  ],
  "include_features": true
}
```

**Response** (~45KB):
- Full details for all 3 classes
- Combined ~180 features
- All translations

**Note**: May hit token limits for LLM context - use `include_features: false` for large batches.

---

## Next Steps

- Review [README.md](README.md) for installation
- Check [TESTING.md](TESTING.md) for verification steps
- See [CLAUDE.md](CLAUDE.md) for development notes
- Explore the [ETIM API documentation](https://etimapi.etim-international.com/swagger/)

Happy integrating! 🎉
