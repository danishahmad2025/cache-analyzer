from db_setup import load_medicare_data
from cache import flush_cache
from benchmark import benchmark_with_and_without_cache
from visualize import plot_results

if __name__ == "__main__":
    print("=== Medicare Claims Cache Analyzer ===")
    print("Dataset: US Medicare Inpatient Hospital Claims\n")

    load_medicare_data()      # Load CSV → SQLite
    flush_cache()             # Clean start
    db_times, cache_times = benchmark_with_and_without_cache()
    plot_results(db_times, cache_times)

    print("\nDone. Check results.png for the speed comparison chart.")
