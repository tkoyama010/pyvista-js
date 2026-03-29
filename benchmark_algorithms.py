#!/usr/bin/env python
"""Benchmark Python algorithms vs TypeScript implementations."""

import time

import numpy as np

from pyvista_js.algorithms import (
    clip_mesh,
    compute_contour,
    create_cone,
    create_cube,
    create_cylinder,
    create_sphere,
    shrink_mesh,
)


def benchmark_sphere():
    """Benchmark sphere creation."""
    print("Benchmarking sphere creation...")

    # Test different resolutions
    resolutions = [8, 16, 32, 64]
    times = []

    for res in resolutions:
        start_time = time.time()
        points, faces = create_sphere(radius=1.0, theta_resolution=res, phi_resolution=res)
        end_time = time.time()

        elapsed = end_time - start_time
        times.append(elapsed)
        print(
            f"  Resolution {res}x{res}: {elapsed:.4f}s ({len(points)} points, {len(faces)} face elements)",
        )

    return times


def benchmark_cone():
    """Benchmark cone creation."""
    print("Benchmarking cone creation...")

    resolutions = [8, 16, 32, 64]
    times = []

    for res in resolutions:
        start_time = time.time()
        points, faces = create_cone(radius=1.0, height=2.0, resolution=res)
        end_time = time.time()

        elapsed = end_time - start_time
        times.append(elapsed)
        print(
            f"  Resolution {res}: {elapsed:.4f}s ({len(points)} points, {len(faces)} face elements)",
        )

    return times


def benchmark_cube():
    """Benchmark cube creation."""
    print("Benchmarking cube creation...")

    sizes = [1.0, 2.0, 5.0, 10.0]
    times = []

    for size in sizes:
        start_time = time.time()
        points, faces = create_cube(size=size)
        end_time = time.time()

        elapsed = end_time - start_time
        times.append(elapsed)
        print(f"  Size {size}: {elapsed:.4f}s ({len(points)} points, {len(faces)} face elements)")

    return times


def benchmark_cylinder():
    """Benchmark cylinder creation."""
    print("Benchmarking cylinder creation...")

    resolutions = [8, 16, 32, 64]
    times = []

    for res in resolutions:
        start_time = time.time()
        points, faces = create_cylinder(radius=1.0, height=2.0, resolution=res)
        end_time = time.time()

        elapsed = end_time - start_time
        times.append(elapsed)
        print(
            f"  Resolution {res}: {elapsed:.4f}s ({len(points)} points, {len(faces)} face elements)",
        )

    return times


def benchmark_shrink():
    """Benchmark mesh shrinking."""
    print("Benchmarking mesh shrinking...")

    # Create test meshes of different sizes
    mesh_sizes = [100, 500, 1000, 5000]
    times = []

    for size in mesh_sizes:
        # Create random points
        points = np.random.randn(size, 3).tolist()

        start_time = time.time()
        result = shrink_mesh(points, shrink_factor=0.8)
        end_time = time.time()

        elapsed = end_time - start_time
        times.append(elapsed)
        print(f"  Mesh size {size}: {elapsed:.4f}s")

    return times


def benchmark_clip():
    """Benchmark mesh clipping."""
    print("Benchmarking mesh clipping...")

    # Create test meshes
    mesh_sizes = [100, 500, 1000, 2000]
    times = []

    for size in mesh_sizes:
        # Create random points and simple faces
        points = np.random.randn(size, 3).tolist()
        faces = []
        for i in range(0, size - 3, 3):
            faces.extend([3, i, i + 1, i + 2])

        start_time = time.time()
        result_points, result_faces = clip_mesh(
            points,
            faces,
            plane_origin=[0, 0, 0],
            plane_normal=[0, 0, 1],
        )
        end_time = time.time()

        elapsed = end_time - start_time
        times.append(elapsed)
        print(f"  Mesh size {size}: {elapsed:.4f}s ({len(result_points)} points after clipping)")

    return times


def benchmark_contour():
    """Benchmark contour computation."""
    print("Benchmarking contour computation...")

    # Create test data
    mesh_sizes = [100, 500, 1000, 5000]
    times = []

    for size in mesh_sizes:
        points = np.random.randn(size, 3).tolist()
        values = np.random.rand(size).tolist()

        start_time = time.time()
        result = compute_contour(points, values, isovalue=0.5)
        end_time = time.time()

        elapsed = end_time - start_time
        times.append(elapsed)
        print(f"  Data size {size}: {elapsed:.4f}s ({len(result)} contour points)")

    return times


def main():
    """Run all benchmarks."""
    print("Python Algorithms Performance Benchmark")
    print("=" * 50)

    results = {}

    results["sphere"] = benchmark_sphere()
    print()

    results["cone"] = benchmark_cone()
    print()

    results["cube"] = benchmark_cube()
    print()

    results["cylinder"] = benchmark_cylinder()
    print()

    results["shrink"] = benchmark_shrink()
    print()

    results["clip"] = benchmark_clip()
    print()

    results["contour"] = benchmark_contour()
    print()

    # Summary
    print("Summary")
    print("=" * 50)
    for algo, times in results.items():
        avg_time = np.mean(times)
        print(f"{algo}: average {avg_time:.4f}s")

    return results


if __name__ == "__main__":
    main()
