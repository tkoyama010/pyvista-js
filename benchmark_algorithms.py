"""Performance benchmarks comparing TypeScript and Python algorithm implementations."""

import time
import numpy as np
from pyvista_js.algorithms import (
    GeometricAlgorithms,
    MeshProcessingAlgorithms,
    create_sphere_source,
    create_cone_source,
    create_cube_source,
    create_cylinder_source,
    apply_shrink_filter_source,
    apply_clip_filter_source,
    apply_contour_filter_source,
)


class AlgorithmBenchmark:
    """Benchmark suite for comparing algorithm performance."""

    def __init__(self):
        self.results = {}

    def benchmark_geometric_algorithms(self):
        """Benchmark geometric primitive generation algorithms."""
        print("=== Geometric Algorithms Benchmark ===")

        # Sphere creation benchmark
        print("\nSphere Creation:")
        sphere_times = []
        for i in range(100):
            start_time = time.time()
            result = GeometricAlgorithms.create_sphere(
                center=(0.0, 0.0, 0.0), radius=1.0, theta_resolution=32, phi_resolution=32
            )
            end_time = time.time()
            sphere_times.append(end_time - start_time)

        avg_sphere_time = np.mean(sphere_times) * 1000  # Convert to milliseconds
        print(f"Average time: {avg_sphere_time:.3f} ms")
        print(f"Min time: {min(sphere_times) * 1000:.3f} ms")
        print(f"Max time: {max(sphere_times) * 1000:.3f} ms")
        self.results["sphere_creation"] = {
            "avg_ms": avg_sphere_time,
            "min_ms": min(sphere_times) * 1000,
            "max_ms": max(sphere_times) * 1000,
            "times": sphere_times,
        }

        # Cone creation benchmark
        print("\nCone Creation:")
        cone_times = []
        for i in range(100):
            start_time = time.time()
            result = GeometricAlgorithms.create_cone(height=1.0, radius=0.5, resolution=32)
            end_time = time.time()
            cone_times.append(end_time - start_time)

        avg_cone_time = np.mean(cone_times) * 1000
        print(f"Average time: {avg_cone_time:.3f} ms")
        print(f"Min time: {min(cone_times) * 1000:.3f} ms")
        print(f"Max time: {max(cone_times) * 1000:.3f} ms")
        self.results["cone_creation"] = {
            "avg_ms": avg_cone_time,
            "min_ms": min(cone_times) * 1000,
            "max_ms": max(cone_times) * 1000,
            "times": cone_times,
        }

        # Cube creation benchmark
        print("\nCube Creation:")
        cube_times = []
        for i in range(100):
            start_time = time.time()
            result = GeometricAlgorithms.create_cube(x_length=1.0, y_length=1.0, z_length=1.0)
            end_time = time.time()
            cube_times.append(end_time - start_time)

        avg_cube_time = np.mean(cube_times) * 1000
        print(f"Average time: {avg_cube_time:.3f} ms")
        print(f"Min time: {min(cube_times) * 1000:.3f} ms")
        print(f"Max time: {max(cube_times) * 1000:.3f} ms")
        self.results["cube_creation"] = {
            "avg_ms": avg_cube_time,
            "min_ms": min(cube_times) * 1000,
            "max_ms": max(cube_times) * 1000,
            "times": cube_times,
        }

        # Cylinder creation benchmark
        print("\nCylinder Creation:")
        cylinder_times = []
        for i in range(100):
            start_time = time.time()
            result = GeometricAlgorithms.create_cylinder(height=1.0, radius=0.5, resolution=32)
            end_time = time.time()
            cylinder_times.append(end_time - start_time)

        avg_cylinder_time = np.mean(cylinder_times) * 1000
        print(f"Average time: {avg_cylinder_time:.3f} ms")
        print(f"Min time: {min(cylinder_times) * 1000:.3f} ms")
        print(f"Max time: {max(cylinder_times) * 1000:.3f} ms")
        self.results["cylinder_creation"] = {
            "avg_ms": avg_cylinder_time,
            "min_ms": min(cylinder_times) * 1000,
            "max_ms": max(cylinder_times) * 1000,
            "times": cylinder_times,
        }

    def benchmark_mesh_processing_algorithms(self):
        """Benchmark mesh processing algorithms."""
        print("\n=== Mesh Processing Algorithms Benchmark ===")

        # Create test mesh (cube)
        cube = GeometricAlgorithms.create_cube(x_length=2.0, y_length=2.0, z_length=2.0)
        points = cube["points"]
        polys = cube["polys"]

        # Shrink filter benchmark
        print("\nShrink Filter:")
        shrink_times = []
        for i in range(100):
            start_time = time.time()
            result = MeshProcessingAlgorithms.apply_shrink_filter(points, polys, shrink_factor=0.8)
            end_time = time.time()
            shrink_times.append(end_time - start_time)

        avg_shrink_time = np.mean(shrink_times) * 1000
        print(f"Average time: {avg_shrink_time:.3f} ms")
        print(f"Min time: {min(shrink_times) * 1000:.3f} ms")
        print(f"Max time: {max(shrink_times) * 1000:.3f} ms")
        self.results["shrink_filter"] = {
            "avg_ms": avg_shrink_time,
            "min_ms": min(shrink_times) * 1000,
            "max_ms": max(shrink_times) * 1000,
            "times": shrink_times,
        }

        # Clip filter benchmark
        print("\nClip Filter:")
        clip_times = []
        for i in range(100):
            start_time = time.time()
            result = MeshProcessingAlgorithms.apply_clip_filter(
                points, polys, normal=(0.0, 0.0, 1.0), origin=(0.0, 0.0, 0.0), invert=False
            )
            end_time = time.time()
            clip_times.append(end_time - start_time)

        avg_clip_time = np.mean(clip_times) * 1000
        print(f"Average time: {avg_clip_time:.3f} ms")
        print(f"Min time: {min(clip_times) * 1000:.3f} ms")
        print(f"Max time: {max(clip_times) * 1000:.3f} ms")
        self.results["clip_filter"] = {
            "avg_ms": avg_clip_time,
            "min_ms": min(clip_times) * 1000,
            "max_ms": max(clip_times) * 1000,
            "times": clip_times,
        }

        # Contour filter benchmark
        print("\nContour Filter:")
        # Create scalar data for contouring
        scalar_data = np.random.rand(points.shape[0])
        values = [0.3, 0.6, 0.9]

        contour_times = []
        for i in range(100):
            start_time = time.time()
            result = MeshProcessingAlgorithms.apply_contour_filter(
                points, polys, scalar_data, values
            )
            end_time = time.time()
            contour_times.append(end_time - start_time)

        avg_contour_time = np.mean(contour_times) * 1000
        print(f"Average time: {avg_contour_time:.3f} ms")
        print(f"Min time: {min(contour_times) * 1000:.3f} ms")
        print(f"Max time: {max(contour_times) * 1000:.3f} ms")
        self.results["contour_filter"] = {
            "avg_ms": avg_contour_time,
            "min_ms": min(contour_times) * 1000,
            "max_ms": max(contour_times) * 1000,
            "times": contour_times,
        }

    def benchmark_json_serialization(self):
        """Benchmark JSON serialization overhead."""
        print("\n=== JSON Serialization Benchmark ===")

        # Create test sphere
        sphere = GeometricAlgorithms.create_sphere(theta_resolution=32, phi_resolution=32)

        json_times = []
        for i in range(100):
            start_time = time.time()
            json_result = create_sphere_source(theta_resolution=32, phi_resolution=32)
            end_time = time.time()
            json_times.append(end_time - start_time)

        avg_json_time = np.mean(json_times) * 1000
        print(f"JSON serialization average time: {avg_json_time:.3f} ms")
        print(f"Min time: {min(json_times) * 1000:.3f} ms")
        print(f"Max time: {max(json_times) * 1000:.3f} ms")
        self.results["json_serialization"] = {
            "avg_ms": avg_json_time,
            "min_ms": min(json_times) * 1000,
            "max_ms": max(json_times) * 1000,
            "times": json_times,
        }

    def benchmark_memory_usage(self):
        """Benchmark memory usage of algorithms."""
        print("\n=== Memory Usage Benchmark ===")

        import tracemalloc

        # Sphere creation memory usage
        tracemalloc.start()
        sphere = GeometricAlgorithms.create_sphere(theta_resolution=64, phi_resolution=64)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        sphere_memory = peak / 1024 / 1024  # Convert to MB
        print(f"Sphere creation peak memory: {sphere_memory:.2f} MB")
        self.results["sphere_memory_mb"] = sphere_memory

        # Mesh processing memory usage
        tracemalloc.start()
        cube = GeometricAlgorithms.create_cube(x_length=10.0, y_length=10.0, z_length=10.0)
        result = MeshProcessingAlgorithms.apply_shrink_filter(
            cube["points"], cube["polys"], shrink_factor=0.8
        )
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        shrink_memory = peak / 1024 / 1024
        print(f"Shrink filter peak memory: {shrink_memory:.2f} MB")
        self.results["shrink_memory_mb"] = shrink_memory

    def print_summary(self):
        """Print a summary of all benchmark results."""
        print("\n" + "=" * 50)
        print("BENCHMARK SUMMARY")
        print("=" * 50)

        if "sphere_creation" in self.results:
            print(f"Sphere Creation: {self.results['sphere_creation']['avg_ms']:.3f} ms avg")
        if "cone_creation" in self.results:
            print(f"Cone Creation: {self.results['cone_creation']['avg_ms']:.3f} ms avg")
        if "cube_creation" in self.results:
            print(f"Cube Creation: {self.results['cube_creation']['avg_ms']:.3f} ms avg")
        if "cylinder_creation" in self.results:
            print(f"Cylinder Creation: {self.results['cylinder_creation']['avg_ms']:.3f} ms avg")
        if "shrink_filter" in self.results:
            print(f"Shrink Filter: {self.results['shrink_filter']['avg_ms']:.3f} ms avg")
        if "clip_filter" in self.results:
            print(f"Clip Filter: {self.results['clip_filter']['avg_ms']:.3f} ms avg")
        if "contour_filter" in self.results:
            print(f"Contour Filter: {self.results['contour_filter']['avg_ms']:.3f} ms avg")
        if "json_serialization" in self.results:
            print(f"JSON Serialization: {self.results['json_serialization']['avg_ms']:.3f} ms avg")
        if "sphere_memory_mb" in self.results:
            print(f"Sphere Memory: {self.results['sphere_memory_mb']:.2f} MB")
        if "shrink_memory_mb" in self.results:
            print(f"Shrink Filter Memory: {self.results['shrink_memory_mb']:.2f} MB")

    def compare_with_typescript(self, typescript_results):
        """Compare Python results with TypeScript implementation results."""
        print("\n" + "=" * 50)
        print("PYTHON vs TYPESCRIPT COMPARISON")
        print("=" * 50)

        comparisons = [
            ("sphere_creation", "Sphere Creation"),
            ("cone_creation", "Cone Creation"),
            ("cube_creation", "Cube Creation"),
            ("cylinder_creation", "Cylinder Creation"),
            ("shrink_filter", "Shrink Filter"),
            ("clip_filter", "Clip Filter"),
            ("contour_filter", "Contour Filter"),
        ]

        for key, name in comparisons:
            if key in self.results and key in typescript_results:
                python_time = self.results[key]["avg_ms"]
                ts_time = typescript_results[key]["avg_ms"]
                speedup = ts_time / python_time
                print(f"{name}:")
                print(f"  Python: {python_time:.3f} ms")
                print(f"  TypeScript: {ts_time:.3f} ms")
                print(f"  Speedup: {speedup:.2f}x {'faster' if speedup > 1 else 'slower'}")

        return self.results


def main():
    """Run the benchmark suite."""
    benchmark = AlgorithmBenchmark()

    print("Starting pyvista-js algorithms benchmark...")

    # Run benchmarks
    benchmark.benchmark_geometric_algorithms()
    benchmark.benchmark_mesh_processing_algorithms()
    benchmark.benchmark_json_serialization()
    benchmark.benchmark_memory_usage()

    # Print summary
    benchmark.print_summary()

    return benchmark.results


if __name__ == "__main__":
    results = main()

    # Save results to file for later analysis
    import json

    with open("benchmark_results.json", "w") as f:
        # Convert numpy arrays to lists for JSON serialization
        json_results = {}
        for key, value in results.items():
            if isinstance(value, dict) and "times" in value:
                json_results[key] = {
                    "avg_ms": value["avg_ms"],
                    "min_ms": value["min_ms"],
                    "max_ms": value["max_ms"],
                    "times": [float(t) for t in value["times"]],
                }
            else:
                json_results[key] = value
        json.dump(json_results, f, indent=2)

    print("\nBenchmark results saved to benchmark_results.json")
