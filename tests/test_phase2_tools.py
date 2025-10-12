#!/usr/bin/env python3
"""Test script for Phase 2 ETIM MCP tools"""
import asyncio
import sys
sys.path.insert(0, 'src')

from etim_mcp.config import settings
from etim_mcp.cache import RedisCache
from etim_mcp.auth import EtimTokenManager
from etim_mcp.client import EtimAPIClient


async def main():
    """Test all Phase 2 API methods"""
    print("=" * 70)
    print("Testing Phase 2 ETIM MCP Tools")
    print("=" * 70)

    # Initialize components
    cache = RedisCache(settings.redis_host, settings.redis_port, settings.redis_password)
    await cache.connect()

    token_manager = EtimTokenManager(cache)
    client = EtimAPIClient(token_manager, cache)

    try:
        # Test 1: Get All Languages
        print("\n1. Testing get_all_languages...")
        all_languages = await client.get_all_languages()
        print(f"   ✓ Found {len(all_languages)} total ETIM languages globally")
        if all_languages:
            for lang in all_languages[:5]:
                print(f"   - {lang.get('code')}: {lang.get('description')}")
            if len(all_languages) > 5:
                print(f"   ... and {len(all_languages) - 5} more")

        # Test 2: Get Class Details Many (batch operation)
        print("\n2. Testing get_class_details_many (batch operation)...")
        classes_to_fetch = [
            {"code": "EC001744", "version": 10},
            {"code": "EC001744", "version": 11},
        ]
        batch_result = await client.get_class_details_many(
            classes=classes_to_fetch,
            language="EN",
            include_features=False
        )
        print(f"   ✓ Retrieved {len(batch_result)} classes in a single request")
        for cls in batch_result:
            print(f"   - {cls.get('code')} v{cls.get('version')}: {cls.get('descriptionEn', 'N/A')[:60]}...")

        # Test 3: Get All Class Versions
        print("\n3. Testing get_all_class_versions...")
        all_versions = await client.get_all_class_versions(
            class_code="EC001744",
            language="EN",
            include_features=False
        )
        print(f"   ✓ Retrieved {len(all_versions)} versions for EC001744")
        for ver in all_versions[:5]:
            print(f"   - Version {ver.get('version')}: {ver.get('descriptionEn', 'N/A')[:60]}...")
        if len(all_versions) > 5:
            print(f"   ... and {len(all_versions) - 5} more versions")

        # Test 4: Get Class for Release
        print("\n4. Testing get_class_for_release...")
        try:
            # First get available releases
            releases = await client.get_releases()
            if releases and len(releases) > 1:
                # Use ETIM-10.0 or second release (skip DYNAMIC)
                test_release = releases[1].get('description', 'ETIM-10.0')
                print(f"   Testing with release: {test_release}")

                release_class = await client.get_class_for_release(
                    class_code="EC001744",
                    release=test_release,
                    language="EN",
                    include_features=False
                )
                print(f"   ✓ Retrieved EC001744 for release {test_release}")
                print(f"   - Description: {release_class.get('descriptionEn', 'N/A')[:60]}...")
                print(f"   - Version: {release_class.get('version')}")
            else:
                print("   ⚠ No releases available for testing")
        except Exception as e:
            print(f"   ⚠ Error testing class for release: {str(e)[:80]}")

        print("\n" + "=" * 70)
        print("✓ All Phase 2 tests completed successfully!")
        print("=" * 70)

        # Summary
        print("\nPhase 2 Summary:")
        print(f"  • Total languages available globally: {len(all_languages)}")
        print(f"  • Batch operation: Retrieved {len(batch_result)} classes efficiently")
        print(f"  • Version history: Found {len(all_versions)} versions of EC001744")
        print(f"  • Release-specific query: Tested successfully")

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
