import asyncio
import sys
sys.path.insert(0, '/home/debian/AD/backend')
from app.adapters.dfs_adapter import DfsAdapter

async def test():
    adapter = DfsAdapter()
    share, sub_path = adapter._parse_smb_path("\\\\dcser1\\share\\HR", "cii_factory")
    print(f"Share: {share}, SubPath: {sub_path}")
    
    items = await adapter.list_directory("\\\\dcser1\\share\\HR", "cii_factory")
    print(f"Items: {len(items)}")
    for i in items:
        print(f"  {i}")

asyncio.run(test())