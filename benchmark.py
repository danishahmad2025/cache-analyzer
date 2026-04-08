import time
from queries import get_top_procedures_by_state
from cache import get_from_cache, set_in_cache

US_STATES = ["CA", "TX", "NY", "FL", "PA", "OH", "IL", "GA", "NC", "MI"]

def benchmark_with_and_without_cache():
    db_times = []
    cache_times = []

    print("Running benchmark on 10 US states x 5 repetitions each...\n")

    for state in US_STATES:
        cache_key = f"top_procedures:{state}"

        # Run WITHOUT cache (always hits the DB)
        for _ in range(5):
            start = time.perf_counter()
            get_top_procedures_by_state(state)
            db_times.append((time.perf_counter() - start) * 1000)

        # Run WITH cache (first call is a miss, next 4 are hits)
        for i in range(5):
            start = time.perf_counter()
            result = get_from_cache(cache_key)
            if not result:
                result = get_top_procedures_by_state(state)
                set_in_cache(cache_key, [list(r) for r in result])
                status = "miss"
            else:
                status = "hit"
            cache_times.append((time.perf_counter() - start) * 1000)

        print(f"State {state}: done ({status} on last run)")

    avg_db = sum(db_times) / len(db_times)
    avg_cache = sum(cache_times) / len(cache_times)
    speedup = avg_db / avg_cache

    print(f"\nAvg DB time:     {avg_db:.2f} ms")
    print(f"Avg Cache time:  {avg_cache:.2f} ms")
    print(f"Cache is {speedup:.1f}x faster")

    return db_times, cache_times