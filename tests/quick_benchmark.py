"""Quick performance benchmark runner with immediate results output."""

import time
import json
from pathlib import Path
from datetime import datetime
import networkx as nx
from cascadesimulator import pyCascadeGenerator


def benchmark_config(nodes, edges_prob, num_cascades, description, edge_weight=0.1):
    """Run benchmark for a specific configuration."""
    print(f"\n{description}")
    print(f"  Graph: {nodes} nodes, p={edges_prob}, edge_weight={edge_weight}")
    print(f"  Cascades: {num_cascades}")
    
    # Create graph using fast method for large graphs
    print(f"  Creating graph...", end=" ", flush=True)
    start = time.perf_counter()
    if nodes >= 10000:
        # Use fast_gnp_random_graph for large graphs
        graph = nx.fast_gnp_random_graph(nodes, edges_prob, directed=True)
    else:
        graph = nx.erdos_renyi_graph(nodes, edges_prob, directed=True)
    
    # Add edge weights efficiently
    nx.set_edge_attributes(graph, edge_weight, 'weight')
    graph_time = time.perf_counter() - start
    print(f"{graph_time:.3f}s ({len(graph.edges())} edges)")
    
    # Initialize generator
    gen = pyCascadeGenerator(graph, cascade_model="IC")
    gen.cascade_model_.set_random_seed(42)
    
    # Run benchmark
    print(f"  Generating {num_cascades} cascades...", end=" ", flush=True)
    start = time.perf_counter()
    result = gen.generate([0], num_cascades=num_cascades)
    elapsed = time.perf_counter() - start
    
    time_per_cascade = elapsed / num_cascades
    avg_cascade_size = sum(len(c) for c in result) / num_cascades
    min_cascade_size = min(len(c) for c in result)
    max_cascade_size = max(len(c) for c in result)
    total_events = sum(len(c) for c in result)
    
    print(f"{elapsed:.3f}s")
    print(f"  Time per cascade: {time_per_cascade*1000:.4f} ms")
    print(f"  Cascade size: avg={avg_cascade_size:.1f}, min={min_cascade_size}, max={max_cascade_size}")
    print(f"  Total events: {total_events:,} ({total_events/elapsed:.0f} events/sec)")
    print(f"  Throughput: {num_cascades/elapsed:.1f} cascades/sec")
    
    return {
        "description": description,
        "nodes": nodes,
        "edges_prob": edges_prob,
        "edge_weight": edge_weight,
        "num_edges": len(graph.edges()),
        "num_cascades": num_cascades,
        "total_time": elapsed,
        "time_per_cascade_ms": time_per_cascade * 1000,
        "throughput_cascades_per_sec": num_cascades / elapsed,
        "avg_cascade_size": avg_cascade_size,
        "min_cascade_size": min_cascade_size,
        "max_cascade_size": max_cascade_size,
        "total_events": total_events,
        "events_per_sec": total_events / elapsed
    }


def main():
    """Run comprehensive benchmark suite."""
    print("=" * 80)
    print("CascadeSimulator Performance Benchmark")
    print("=" * 80)
    
    results = []
    
    # Configuration: (nodes, edge_prob, num_cascades, description, edge_weight)
    configs = [
        (100, 0.05, 1000, "Tiny graph (100 nodes) - 1000 cascades", 0.1),
        (1000, 0.01, 1000, "Small graph (1,000 nodes) - 1000 cascades", 0.1),
        (1000, 0.01, 100, "Small graph (1,000 nodes) - 100 cascades", 0.1),
        (10000, 0.001, 100, "Medium graph (10,000 nodes) - 100 cascades", 0.1),
        (10000, 0.001, 10, "Medium graph (10,000 nodes) - 10 cascades", 0.1),
        # Note: 100k nodes takes very long for graph creation, skipping for now
        # (100000, 0.0001, 10, "Large graph (100,000 nodes) - 10 cascades", 0.1),
        # (100000, 0.0001, 1, "Large graph (100,000 nodes) - 1 cascade", 0.1),
    ]
    
    for config in configs:
        try:
            result = benchmark_config(*config)
            results.append(result)
        except KeyboardInterrupt:
            print("\n\nBenchmark interrupted by user")
            break
        except Exception as e:
            print(f"\n  ERROR: {e}")
            continue
    
    # Save results
    results_dir = Path(__file__).parent / "benchmarks" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = results_dir / f"benchmark_v0.1.0_{timestamp}.json"
    
    data = {
        "version": "0.1.0",
        "timestamp": datetime.now().isoformat(),
        "results": results
    }
    
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    for r in results:
        print(f"{r['description']:50s} {r['time_per_cascade_ms']:8.4f} ms/cascade")
    
    print(f"\nResults saved to: {json_file}")
    
    # Create markdown summary
    md_file = results_dir / f"summary_v0.1.0_{timestamp}.md"
    with open(md_file, 'w') as f:
        f.write("# CascadeSimulator Performance Benchmark\n\n")
        f.write(f"**Version:** 0.1.0  \n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n\n")
        
        f.write("## Results\n\n")
        f.write("| Configuration | Nodes | Edges | Cascades | Time/Cascade | Events | Throughput |\n")
        f.write("|--------------|-------|-------|----------|--------------|--------|------------|\n")
        
        for r in results:
            f.write(f"| {r['description']:40s} | {r['nodes']:,} | {r['num_edges']:,} | "
                   f"{r['num_cascades']:,} | {r['time_per_cascade_ms']:.4f} ms | "
                   f"{r['total_events']:,} | {r['throughput_cascades_per_sec']:.1f}/s |\n")
        
        f.write("\n## Detailed Results\n\n")
        for r in results:
            f.write(f"### {r['description']}\n\n")
            f.write(f"- **Nodes:** {r['nodes']:,}\n")
            f.write(f"- **Edges:** {r['num_edges']:,}\n")
            f.write(f"- **Edge Weight:** {r['edge_weight']}\n")
            f.write(f"- **Cascades:** {r['num_cascades']:,}\n")
            f.write(f"- **Total Time:** {r['total_time']:.3f}s\n")
            f.write(f"- **Time per Cascade:** {r['time_per_cascade_ms']:.4f} ms\n")
            f.write(f"- **Throughput:** {r['throughput_cascades_per_sec']:.1f} cascades/sec\n")
            f.write(f"- **Total Events:** {r['total_events']:,}\n")
            f.write(f"- **Events per Second:** {r['events_per_sec']:.1f}\n")
            f.write(f"- **Avg Cascade Size:** {r['avg_cascade_size']:.1f} nodes (min: {r['min_cascade_size']}, max: {r['max_cascade_size']})\n\n")
    
    print(f"Summary saved to: {md_file}")


if __name__ == "__main__":
    main()
