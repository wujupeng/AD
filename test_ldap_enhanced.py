import asyncio
import sys
sys.path.insert(0, '/home/debian/AD/backend')
from app.adapters.ldap_adapter import LdapAdapter

async def test():
    adapter = LdapAdapter()
    
    print("=== Test 1: RPC bind with valid credentials (CII domain) ===")
    result = await adapter.bind("Administrator", "*****")
    print(f"Result: {result}")
    
    print("\n=== Test 2: RPC bind with invalid password ===")
    result2 = await adapter.bind("Administrator", "WrongPassword123")
    print(f"Result: {result2}")
    
    print("\n=== Test 3: RPC bind with non-existent user ===")
    result3 = await adapter.bind("nonexistent_user", "*****")
    print(f"Result: {result3}")
    
    print("\n=== Test 4: Search users in CII domain ===")
    results = await adapter.search("DC=cii,DC=sh,DC=cn", "(objectClass=user)", ["sAMAccountName", "displayName"])
    print(f"Users found: {len(results)}")
    for r in results[:5]:
        print(f"  {r.get('sAMAccountName', 'N/A')}: {r.get('displayName', 'N/A')}")
    
    print("\n=== Test 5: Search groups in CII domain ===")
    results2 = await adapter.search("DC=cii,DC=sh,DC=cn", "(objectClass=group)", ["sAMAccountName"])
    print(f"Groups found: {len(results2)}")
    
    print("\n=== Test 6: Health check for CII factory ===")
    health = await adapter.health_check("cii_factory")
    print(f"Health: {health}")
    
    print("\n=== Test 7: Health check for HQ (default) ===")
    health2 = await adapter.health_check()
    print(f"Health: {health2}")

asyncio.run(test())