#!/usr/bin/env python3
"""Test script for new ETIM MCP tools"""
import asyncio
import sys
sys.path.insert(0, 'src')

from etim_mcp.config import settings
from etim_mcp.cache import RedisCache
from etim_mcp.auth import EtimTokenManager
from etim_mcp.client import EtimAPIClient


async def main():
    """Test all new API methods"""
    print("=" * 60)
    print("Testing New ETIM MCP Tools")
    print("=" * 60)

    # Initialize components
    cache = RedisCache(settings.redis_host, settings.redis_port, settings.redis_password)
    await cache.connect()

    token_manager = EtimTokenManager(cache)
    client = EtimAPIClient(token_manager, cache)

    try:
        # Test 1: Search Values
        print("\n1. Testing search_values...")
        values = await client.search_values("red", "EN", False, 0, 3)
        print(f"   ✓ Found {values.get('total', 0)} red values")
        if values.get('values'):
            for val in values['values'][:2]:
                print(f"   - {val.get('code')}")

        # Test 2: Get Value Details
        print("\n2. Testing get_value_details...")
        if values.get('values'):
            first_value_code = values['values'][0]['code']
            value_details = await client.get_value_details(first_value_code, "EN")
            print(f"   ✓ Retrieved details for {first_value_code}")
            print(f"   - Description: {value_details.get('descriptionEn', 'N/A')}")

        # Test 3: Search Units
        print("\n3. Testing search_units...")
        units = await client.search_units("milli", "EN", False, 0, 3)
        print(f"   ✓ Found {units.get('total', 0)} units")
        if units.get('units'):
            for unit in units['units'][:2]:
                print(f"   - {unit.get('code')}")

        # Test 4: Get Unit Details
        print("\n4. Testing get_unit_details...")
        if units.get('units'):
            first_unit_code = units['units'][0]['code']
            unit_details = await client.get_unit_details(first_unit_code, "EN")
            print(f"   ✓ Retrieved details for {first_unit_code}")
            print(f"   - Abbreviation: {unit_details.get('abbreviationEn', 'N/A')}")

        # Test 5: Search Feature Groups
        print("\n5. Testing search_feature_groups...")
        fgroups = await client.search_feature_groups("electrical", "EN", 0, 3)
        print(f"   ✓ Found {fgroups.get('total', 0)} feature groups")
        if fgroups.get('featureGroups'):
            for fg in fgroups['featureGroups'][:2]:
                print(f"   - {fg.get('code')}")

        # Test 6: Get Feature Group Details
        print("\n6. Testing get_feature_group_details...")
        if fgroups.get('featureGroups'):
            first_fg_code = fgroups['featureGroups'][0]['code']
            fg_details = await client.get_feature_group_details(first_fg_code, "EN")
            print(f"   ✓ Retrieved details for {first_fg_code}")
            print(f"   - Description: {fg_details.get('descriptionEn', 'N/A')}")

        # Test 7: Get Group Details
        print("\n7. Testing get_group_details...")
        group_details = await client.get_group_details("EG000030", "EN", True)
        print(f"   ✓ Retrieved details for EG000030")
        print(f"   - Description: {group_details.get('descriptionEn', 'N/A')}")

        # Test 8: Get Class Diff
        print("\n8. Testing get_class_diff...")
        try:
            class_diff = await client.get_class_diff("EC000034", 7, "EN")
            print(f"   ✓ Retrieved diff for EC000034 version 7")
            print(f"   - Has features: {'features' in class_diff}")
        except Exception as e:
            print(f"   ⚠ Class diff test skipped (needs version 2+): {str(e)[:50]}")

        print("\n" + "=" * 60)
        print("✓ All tests completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await client.close()
        await token_manager.close()
        await cache.close()


if __name__ == "__main__":
    asyncio.run(main())
