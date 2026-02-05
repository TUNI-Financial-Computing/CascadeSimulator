"""Script to run benchmarks and save performance results."""

import subprocess
import json
import time
from pathlib import Path
from datetime import datetime


def run_benchmarks_and_save():
    """Run all benchmarks and save results with version tracking."""
    
    # Get version from pyproject.toml
    import tomli
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    with open(pyproject_path, 'rb') as f:
        config = tomli.load(f)
        version = config['project']['version']
    
    print(f"Running benchmarks for version {version}...")
    print("=" * 80)
    
    # Run pytest-benchmark and save JSON output
    results_dir = Path(__file__).parent / "benchmarks" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = results_dir / f"benchmark_v{version}_{timestamp}.json"
    
    # Run benchmarks with JSON export
    cmd = [
        "pytest",
        "tests/benchmarks/benchmark_scaling.py",
        "-v",
        "--benchmark-only",
        "--benchmark-json", str(json_file),
        "--benchmark-warmup=on",
        "--benchmark-min-rounds=5"
    ]
    
    print(f"Command: {' '.join(cmd)}\n")
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - start_time
    
    # Print output
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    print(f"\nTotal benchmark time: {elapsed:.2f} seconds")
    
    # Load and summarize results
    if json_file.exists():
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        print(f"\nResults saved to: {json_file}")
        print("\nSummary:")
        print("-" * 80)
        
        benchmarks = data.get('benchmarks', [])
        for bench in benchmarks:
            name = bench['name']
            stats = bench['stats']
            mean = stats['mean'] * 1000  # Convert to ms
            stddev = stats['stddev'] * 1000
            min_time = stats['min'] * 1000
            max_time = stats['max'] * 1000
            
            print(f"{name:60s}: {mean:8.3f} ms ± {stddev:6.3f} ms")
            print(f"{'':60s}  [min: {min_time:.3f} ms, max: {max_time:.3f} ms]")
        
        # Create summary file
        summary_file = results_dir / f"summary_v{version}_{timestamp}.txt"
        with open(summary_file, 'w') as f:
            f.write(f"CascadeSimulator Benchmark Results\n")
            f.write(f"Version: {version}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'=' * 80}\n\n")
            
            for bench in benchmarks:
                name = bench['name']
                stats = bench['stats']
                mean = stats['mean'] * 1000
                stddev = stats['stddev'] * 1000
                
                f.write(f"{name}\n")
                f.write(f"  Mean: {mean:.3f} ms ± {stddev:.3f} ms\n")
                f.write(f"  Min:  {stats['min']*1000:.3f} ms\n")
                f.write(f"  Max:  {stats['max']*1000:.3f} ms\n")
                f.write(f"  Rounds: {stats['rounds']}\n\n")
        
        print(f"\nSummary saved to: {summary_file}")
    
    return result.returncode == 0


if __name__ == "__main__":
    try:
        import tomli
    except ImportError:
        print("Installing tomli for reading pyproject.toml...")
        subprocess.run(["pip", "install", "tomli"], check=True)
        import tomli
    
    success = run_benchmarks_and_save()
    exit(0 if success else 1)
