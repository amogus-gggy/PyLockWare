"""
Async Test Project for PyLockWare
Tests async/await, decorators, type annotations, and various Python features
"""
import asyncio
from typing import List, Dict, Optional, Callable, Any
from functools import wraps
import time


# Test decorator obfuscation
def timing_decorator(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper


def retry_decorator(max_retries: int = 3):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {e}")
                    if attempt == max_retries - 1:
                        raise
                    await asyncio.sleep(1)
        return wrapper
    return decorator


class AsyncDataProcessor:
    """Async data processor with type annotations"""
    
    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data
        self.processed_data: List[Dict[str, Any]] = []
        self._cache: Dict[str, Any] = {}
    
    async def process_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single item asynchronously"""
        await asyncio.sleep(0.01)  # Simulate async work
        processed = {k: v.upper() if isinstance(v, str) else v for k, v in item.items()}
        return processed
    
    async def process_all(self) -> List[Dict[str, Any]]:
        """Process all items asynchronously"""
        tasks = [self.process_item(item) for item in self.data]
        self.processed_data = await asyncio.gather(*tasks)
        return self.processed_data
    
    async def process_with_cache(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Process item with caching"""
        if item_id in self._cache:
            return self._cache[item_id]
        
        item = next((d for d in self.data if d.get('id') == item_id), None)
        if item:
            processed = await self.process_item(item)
            self._cache[item_id] = processed
            return processed
        return None


@timing_decorator
@retry_decorator(max_retries=2)
async def fetch_data(url: str) -> Dict[str, Any]:
    """Simulate async data fetching"""
    await asyncio.sleep(0.1)
    return {"url": url, "data": f"Response from {url}", "status": 200}


@timing_decorator
async def process_pipeline(data: List[int]) -> List[int]:
    """Async pipeline with multiple transformations"""
    async def transform(x: int) -> int:
        await asyncio.sleep(0.01)
        return x * 2 + 1
    
    tasks = [transform(x) for x in data]
    results = await asyncio.gather(*tasks)
    return list(results)


async def main():
    """Main async function with comprehensive async patterns"""
    
    # Test async data processor
    test_data = [
        {"id": "1", "name": "alice", "value": 10},
        {"id": "2", "name": "bob", "value": 20},
        {"id": "3", "name": "charlie", "value": 30},
    ]
    
    processor = AsyncDataProcessor(test_data)
    results = await processor.process_all()
    print(f"Processed {len(results)} items")
    
    # Test async for
    async def async_generator(n: int):
        for i in range(n):
            await asyncio.sleep(0.01)
            yield i
    
    print("Async generator results:")
    async for value in async_generator(5):
        print(f"  Generated: {value}")
    
    # Test async with
    class AsyncContextManager:
        async def __aenter__(self):
            print("Entering async context")
            return self
        
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            print("Exiting async context")
    
    async with AsyncContextManager():
        print("Inside async context")
    
    # Test fetch with decorators
    results = await asyncio.gather(
        fetch_data("http://api.example.com/1"),
        fetch_data("http://api.example.com/2"),
        fetch_data("http://api.example.com/3"),
    )
    print(f"Fetched {len(results)} responses")
    
    # Test pipeline
    pipeline_result = await process_pipeline([1, 2, 3, 4, 5])
    print(f"Pipeline result: {pipeline_result}")
    
    # Test mixed sync/async
    def sync_helper(x: int) -> str:
        return f"Processed {x}"
    
    results = []
    for i in range(3):
        await asyncio.sleep(0.01)
        results.append(sync_helper(i))
    
    print(f"Sync helper results: {results}")
    
    return True


if __name__ == "__main__":
    asyncio.run(main())
