import json
import time
import os
import csv
import gc
import psutil
import random
import string
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Any
from enum import Enum
import numpy as np

# Create results directory if it doesn't exist
os.makedirs("results", exist_ok=True)

# CSV file setup
CSV_FILE = "results/json_type_comparison.csv"
csv_headers = [
    "type_category",
    "specific_type",
    "n_objects",
    "serialization_time",
    "deserialization_time",
    "serialized_size_mb",
    "mem_usage_mb",
    "speed_mb_per_sec",
]

# Initialize CSV file with headers
with open(CSV_FILE, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=csv_headers)
    writer.writeheader()


def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process()
    return process.memory_info().rss / (1024 * 1024)


def write_to_csv(
    type_category,
    specific_type,
    n_objects,
    serialization_time,
    deserialization_time,
    serialized_size_mb,
    mem_usage_mb,
    speed_mb_per_sec,
):
    """Write a single row to CSV file"""
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_headers)
        writer.writerow(
            {
                "type_category": type_category,
                "specific_type": specific_type,
                "n_objects": n_objects,
                "serialization_time": round(serialization_time, 4),
                "deserialization_time": round(deserialization_time, 4),
                "serialized_size_mb": round(serialized_size_mb, 2),
                "mem_usage_mb": round(mem_usage_mb, 2),
                "speed_mb_per_sec": round(speed_mb_per_sec, 2),
            }
        )


# ============================================================================
# Define test data structures for different type categories
# ============================================================================


class DataType(Enum):
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    BOOL = "bool"
    NULL = "null"
    LIST = "list"
    DICT = "dict"
    MIXED = "mixed"


# Test data generators for different types
class TypeGenerators:
    @staticmethod
    def generate_ints(n: int) -> List[int]:
        """Generate integer data"""
        return list(range(n))

    @staticmethod
    def generate_floats(n: int) -> List[float]:
        """Generate float data with various precisions"""
        return [float(i) * 1.23456789 for i in range(n)]

    @staticmethod
    def generate_strings(n: int, length_range=(10, 100)) -> List[str]:
        """Generate strings of varying lengths"""
        strings = []
        for i in range(n):
            length = random.randint(*length_range)
            # Mix of alphanumeric and special characters
            chars = string.ascii_letters + string.digits + string.punctuation
            strings.append("".join(random.choices(chars, k=length)))
        return strings

    @staticmethod
    def generate_bools(n: int) -> List[bool]:
        """Generate boolean data"""
        return [i % 2 == 0 for i in range(n)]

    @staticmethod
    def generate_nulls(n: int) -> List[None]:
        """Generate null values"""
        return [None] * n

    @staticmethod
    def generate_lists(n: int, list_size_range=(3, 10)) -> List[List[int]]:
        """Generate lists of varying sizes"""
        lists = []
        for i in range(n):
            size = random.randint(*list_size_range)
            lists.append(list(range(i, i + size)))
        return lists

    @staticmethod
    def generate_dicts(n: int, dict_size_range=(2, 5)) -> List[Dict]:
        """Generate dictionaries with varying keys"""
        dicts = []
        for i in range(n):
            size = random.randint(*dict_size_range)
            d = {}
            for j in range(size):
                key = f"key_{j}"
                value = random.randint(0, 1000)
                d[key] = value
            dicts.append(d)
        return dicts

    @staticmethod
    def generate_mixed(n: int) -> List[Any]:
        """Generate mixed type data"""
        mixed = []
        types = [int, float, str, bool, list, dict, None]
        for i in range(n):
            data_type = random.choice(types)
            if data_type is int:
                mixed.append(i)
            elif data_type is float:
                mixed.append(float(i) * 1.5)
            elif data_type is str:
                mixed.append(f"mixed_string_{i}")
            elif data_type is bool:
                mixed.append(i % 2 == 0)
            elif data_type is list:
                mixed.append([i, i + 1, i + 2])
            elif data_type is dict:
                mixed.append({"id": i, "value": i * 2})
            else:  # None
                mixed.append(None)
        return mixed

    @staticmethod
    def generate_complex_objects(n: int) -> List[Dict]:
        """Generate complex nested objects"""
        objects = []
        for i in range(n):
            obj = {
                "id": i,
                "name": f"object_{i}",
                "metadata": {
                    "created": datetime.now().isoformat(),
                    "tags": [f"tag_{i % 10}", f"cat_{i % 5}"],
                    "score": float(i) / 100,
                    "active": i % 2 == 0,
                    "nested": {"level2": {"level3": i * 2, "data": [1, 2, 3, 4, 5]}},
                },
                "coordinates": {
                    "x": random.random(),
                    "y": random.random(),
                    "z": random.random(),
                },
                "history": [i - 3, i - 2, i - 1, i] if i > 3 else [0, 1, i],
                "flags": [True, False, True] if i % 3 == 0 else [False, False, True],
            }
            objects.append(obj)
        return objects

    @staticmethod
    def generate_special_numbers(n: int) -> List[float]:
        """Generate special numeric values (inf, nan, large numbers)"""
        specials = []
        for i in range(n):
            choice = i % 5
            if choice == 0:
                specials.append(float("inf"))
            elif choice == 1:
                specials.append(float("-inf"))
            elif choice == 2:
                specials.append(float("nan"))
            elif choice == 3:
                specials.append(1e308)  # Very large number
            else:
                specials.append(1e-308)  # Very small number
        return specials

    @staticmethod
    def generate_unicode_strings(n: int) -> List[str]:
        """Generate Unicode strings with various scripts"""
        unicode_samples = [
            "Hello世界",
            "Привет мир",
            "مرحبا بالعالم",
            "नमस्ते दुनिया",
            "こんにちは世界",
            "안녕하세요 세계",
            "δημοκρατία",
            "𐤀𐤋𐤐𐤁𐤉𐤕",
            "🎉🚀💻🐍",
            "éèêëàâäôöûüÿçñ",
            "🦊🚀🐍📦🔥",
            "𝕳𝖊𝖑𝖑𝖔 𝖂𝖔𝖗𝖑𝖉",
            "𝓗𝓮𝓵𝓵𝓸 𝓦𝓸𝓻𝓵𝓭",
            "𝕄𝕒𝕥𝕙 𝕋𝕖𝕩𝕥",
            "🇺🇳🌍🌎🌏",
        ]
        return [random.choice(unicode_samples) + f"_{i}" for i in range(n)]


# ============================================================================
# JSON Serialization wrapper
# ============================================================================
class JSONSerializer:
    @staticmethod
    def serialize(obj):
        class CustomEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                if isinstance(obj, date):
                    return obj.isoformat()
                if isinstance(obj, Decimal):
                    return float(obj)
                if isinstance(obj, np.integer):
                    return int(obj)
                if isinstance(obj, np.floating):
                    return float(obj)
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                if isinstance(obj, Enum):
                    return obj.value
                return super().default(obj)

        return json.dumps(obj, cls=CustomEncoder).encode("utf-8")

    @staticmethod
    def deserialize(data):
        return json.loads(data.decode("utf-8"))


# ============================================================================
# Benchmark function for specific type
# ============================================================================
def benchmark_type(
    type_category: str, specific_type: str, data_generator, n_objects: int
):
    """Benchmark JSON serialization for a specific data type"""

    print(f"\n  Testing {specific_type}...", end=" ", flush=True)

    # Generate data
    gc.collect()
    mem_before = get_memory_usage()
    start_time = time.time()

    data = data_generator(n_objects)
    _ = time.time() - start_time

    # Serialization
    start_time = time.time()
    serialized = JSONSerializer.serialize(data)
    serialization_time = time.time() - start_time

    # Deserialization
    start_time = time.time()
    deserialized = JSONSerializer.deserialize(serialized)
    deserialization_time = time.time() - start_time

    # Verify data integrity (partial verification for performance)
    if len(deserialized) == len(data):
        verification = " Ok"
    else:
        verification = "✗"

    mem_after = get_memory_usage()
    mem_used = mem_after - mem_before
    serialized_size_mb = len(serialized) / (1024 * 1024)
    speed = serialized_size_mb / serialization_time if serialization_time > 0 else 0

    write_to_csv(
        type_category=type_category,
        specific_type=specific_type,
        n_objects=n_objects,
        serialization_time=serialization_time,
        deserialization_time=deserialization_time,
        serialized_size_mb=serialized_size_mb,
        mem_usage_mb=mem_used,
        speed_mb_per_sec=speed,
    )

    print(
        f"{verification} Ser: {serialization_time:.3f}s, Deser: {deserialization_time:.3f}s, "
        f"Size: {serialized_size_mb:.1f}MB, Mem: {mem_used:.1f}MB",
        flush=True,
    )

    # Clean up
    del data, serialized, deserialized
    gc.collect()

    return {
        "type": specific_type,
        "serialization_time": serialization_time,
        "deserialization_time": deserialization_time,
        "size_mb": serialized_size_mb,
        "mem_mb": mem_used,
        "speed": speed,
    }


# ============================================================================
# Main benchmark function
# ============================================================================
def run_json_type_benchmarks():
    """Run benchmarks for all JSON data types"""

    N_OBJECTS = 100_000  # 100k objects for reasonable test time

    print("=" * 80)
    print("JSON SERIALIZATION TYPE COMPARISON BENCHMARK")
    print(f"Number of objects per test: {N_OBJECTS:,}")
    print("=" * 80)

    # Define all type tests
    type_tests = [
        # Primitive types
        ("Primitive", "integers", lambda n: TypeGenerators.generate_ints(n)),
        ("Primitive", "floats", lambda n: TypeGenerators.generate_floats(n)),
        (
            "Primitive",
            "strings_short",
            lambda n: TypeGenerators.generate_strings(n, (10, 30)),
        ),
        (
            "Primitive",
            "strings_medium",
            lambda n: TypeGenerators.generate_strings(n, (50, 150)),
        ),
        (
            "Primitive",
            "strings_long",
            lambda n: TypeGenerators.generate_strings(n, (200, 500)),
        ),
        (
            "Primitive",
            "unicode_strings",
            lambda n: TypeGenerators.generate_unicode_strings(n),
        ),
        ("Primitive", "booleans", lambda n: TypeGenerators.generate_bools(n)),
        ("Primitive", "nulls", lambda n: TypeGenerators.generate_nulls(n)),
        # Special numbers
        (
            "Special",
            "special_numbers",
            lambda n: TypeGenerators.generate_special_numbers(n),
        ),
        # Collections
        (
            "Collections",
            "lists_small",
            lambda n: TypeGenerators.generate_lists(n, (2, 5)),
        ),
        (
            "Collections",
            "lists_medium",
            lambda n: TypeGenerators.generate_lists(n, (10, 20)),
        ),
        (
            "Collections",
            "lists_large",
            lambda n: TypeGenerators.generate_lists(n, (30, 50)),
        ),
        (
            "Collections",
            "dicts_small",
            lambda n: TypeGenerators.generate_dicts(n, (1, 3)),
        ),
        (
            "Collections",
            "dicts_medium",
            lambda n: TypeGenerators.generate_dicts(n, (5, 10)),
        ),
        (
            "Collections",
            "dicts_large",
            lambda n: TypeGenerators.generate_dicts(n, (15, 25)),
        ),
        # Complex structures
        ("Complex", "mixed_types", lambda n: TypeGenerators.generate_mixed(n)),
        (
            "Complex",
            "complex_objects",
            lambda n: TypeGenerators.generate_complex_objects(n),
        ),
    ]

    results = []

    for category, type_name, generator in type_tests:
        try:
            result = benchmark_type(category, type_name, generator, N_OBJECTS)
            results.append(result)
        except Exception as e:
            print(f"\n  ✗ Error testing {type_name}: {e}")
            continue

    return results


# ============================================================================
# Scaling test with different object counts
# ============================================================================
def test_scaling():
    """Test JSON serialization scaling with different object counts"""

    object_counts = [1_000, 10_000, 50_000, 100_000]
    test_types = [
        ("integers", TypeGenerators.generate_ints),
        ("strings_medium", lambda n: TypeGenerators.generate_strings(n, (50, 150))),
        ("complex_objects", TypeGenerators.generate_complex_objects),
    ]

    print("\n" + "=" * 80)
    print("SCALING TEST: JSON Serialization with Different Object Counts")
    print("=" * 80)

    for n_objects in object_counts:
        print(f"\n--- Testing with {n_objects:,} objects ---")

        for type_name, generator in test_types:
            # Create temp CSV entry
            print(f"  {type_name:20}", end=" ", flush=True)

            # Generate data
            gc.collect()
            mem_before = get_memory_usage()
            start_time = time.time()

            data = generator(n_objects)
            _ = time.time() - start_time

            # Serialization
            start_time = time.time()
            serialized = JSONSerializer.serialize(data)
            serialization_time = time.time() - start_time

            # Deserialization
            start_time = time.time()
            deserialized = JSONSerializer.deserialize(serialized)
            deserialization_time = time.time() - start_time

            mem_after = get_memory_usage()
            mem_used = mem_after - mem_before
            size_mb = len(serialized) / (1024 * 1024)

            print(
                f"| Ser: {serialization_time:.2f}s | Deser: {deserialization_time:.2f}s | "
                f"Size: {size_mb:.1f}MB | Mem: {mem_used:.1f}MB"
            )

            # Write to scaling CSV
            scaling_csv = "results/json_scaling_results.csv"
            if not os.path.exists(scaling_csv):
                with open(scaling_csv, "w", newline="") as f:
                    writer = csv.DictWriter(
                        f,
                        fieldnames=[
                            "type",
                            "n_objects",
                            "serialization_time",
                            "deserialization_time",
                            "size_mb",
                            "mem_mb",
                        ],
                    )
                    writer.writeheader()

            with open(scaling_csv, "a", newline="") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "type",
                        "n_objects",
                        "serialization_time",
                        "deserialization_time",
                        "size_mb",
                        "mem_mb",
                    ],
                )
                writer.writerow(
                    {
                        "type": type_name,
                        "n_objects": n_objects,
                        "serialization_time": round(serialization_time, 4),
                        "deserialization_time": round(deserialization_time, 4),
                        "size_mb": round(size_mb, 2),
                        "mem_mb": round(mem_used, 2),
                    }
                )

            del data, serialized, deserialized
            gc.collect()


# ============================================================================
# Memory efficiency test
# ============================================================================
def test_memory_efficiency():
    """Test memory efficiency for different data types"""

    N_OBJECTS = 50_000

    print("\n" + "=" * 80)
    print("MEMORY EFFICIENCY TEST")
    print("=" * 80)

    type_tests = [
        ("integers", TypeGenerators.generate_ints),
        ("floats", TypeGenerators.generate_floats),
        ("strings", lambda n: TypeGenerators.generate_strings(n, (100, 200))),
        ("lists", lambda n: TypeGenerators.generate_lists(n, (5, 15))),
        ("dicts", lambda n: TypeGenerators.generate_dicts(n, (3, 8))),
        ("complex_objects", TypeGenerators.generate_complex_objects),
    ]

    results = []
    for type_name, generator in type_tests:
        print(f"\n  Testing {type_name}...", end=" ", flush=True)

        gc.collect()
        mem_before = get_memory_usage()

        data = generator(N_OBJECTS)
        mem_after_data = get_memory_usage()
        mem_data = mem_after_data - mem_before

        serialized = JSONSerializer.serialize(data)
        mem_after_serialized = get_memory_usage()
        mem_serialized = mem_after_serialized - mem_after_data

        del data, serialized
        gc.collect()

        print(
            f"Data: {mem_data:.1f}MB, Serialized: {mem_serialized:.1f}MB, "
            f"Ratio: {mem_serialized / mem_data:.2f}x"
        )

        results.append(
            {
                "type": type_name,
                "memory_data_mb": mem_data,
                "memory_serialized_mb": mem_serialized,
                "compression_ratio": mem_serialized / mem_data if mem_data > 0 else 0,
            }
        )

    # Save memory results
    with open("results/json_memory_efficiency.csv", "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "type",
                "memory_data_mb",
                "memory_serialized_mb",
                "compression_ratio",
            ],
        )
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    print("JSON Serialization Type Comparison Benchmark")
    print("Testing different data types with JSON serialization")
    print("=" * 80)

    # Check if psutil is installed
    try:
        import psutil
    except ImportError:
        print("ERROR: psutil is required. Install with: pip install psutil")
        exit(1)

    try:
        # Run main benchmarks
        results = run_json_type_benchmarks()

        # Run scaling tests
        test_scaling()

        # Run memory efficiency tests
        test_memory_efficiency()

        print("\n" + "=" * 80)
        print(f"Benchmark completed! Results saved to {CSV_FILE}")
        print("Additional results saved to:")
        print("  - results/json_scaling_results.csv")
        print("  - results/json_memory_efficiency.csv")

    except KeyboardInterrupt:
        print("\n\nBenchmark interrupted by user")
    except Exception as e:
        print(f"\nError occurred: {e}")
        import traceback

        traceback.print_exc()
        raise
