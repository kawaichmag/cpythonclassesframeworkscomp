import msgspec
import time
import os
import csv
import json
import xml.etree.ElementTree as ET
import pickle
import gc
import psutil
from typing import Dict, List, Any
import numpy as np

# Create results directory if it doesn't exist
os.makedirs("results", exist_ok=True)

# CSV file setup
CSV_FILE = "results/format_comparison.csv"
csv_headers = [
    "format",
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
    format_name,
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
                "format": format_name,
                "n_objects": n_objects,
                "serialization_time": round(serialization_time, 4),
                "deserialization_time": round(deserialization_time, 4),
                "serialized_size_mb": round(serialized_size_mb, 2),
                "mem_usage_mb": round(mem_usage_mb, 2),
                "speed_mb_per_sec": round(speed_mb_per_sec, 2),
            }
        )


# ============================================================================
# Define test data structure
# ============================================================================
class TestData(msgspec.Struct):
    id: int
    name: str
    value: float
    active: bool
    tags: List[str]
    metadata: Dict[str, Any]
    score: int


def create_test_data(n_objects: int) -> List[TestData]:
    """Create list of test objects"""
    objects = []
    for i in range(n_objects):
        obj = TestData(
            id=i,
            name=f"object_{i}",
            value=float(i) * 1.5,
            active=i % 2 == 0,
            tags=[f"tag_{i % 10}", f"category_{i % 5}"],
            metadata={"created": i, "version": "1.0", "score": i * 2},
            score=i % 1000,
        )
        objects.append(obj)
    return objects


# ============================================================================
# Format-specific serializers/deserializers
# ============================================================================


class MessagePackSerializer:
    @staticmethod
    def serialize(obj):
        return msgspec.msgpack.encode(obj)

    @staticmethod
    def deserialize(data, obj_type):
        return msgspec.msgpack.decode(data, type=List[obj_type])


class JSONSerializer:
    @staticmethod
    def serialize(obj):
        # Convert msgspec objects to dicts
        if isinstance(obj, list) and all(isinstance(x, msgspec.Struct) for x in obj):
            dict_list = [msgspec.to_builtins(x) for x in obj]
            return json.dumps(dict_list).encode("utf-8")
        return json.dumps(obj).encode("utf-8")

    @staticmethod
    def deserialize(data, obj_type):
        dict_list = json.loads(data.decode("utf-8"))
        return [obj_type(**item) for item in dict_list]


class JSONCompactSerializer:
    """JSON without whitespace for minimal size"""

    @staticmethod
    def serialize(obj):
        if isinstance(obj, list) and all(isinstance(x, msgspec.Struct) for x in obj):
            dict_list = [msgspec.to_builtins(x) for x in obj]
            return json.dumps(dict_list, separators=(",", ":")).encode("utf-8")
        return json.dumps(obj, separators=(",", ":")).encode("utf-8")

    @staticmethod
    def deserialize(data, obj_type):
        dict_list = json.loads(data.decode("utf-8"))
        return [obj_type(**item) for item in dict_list]


class XMLSerializer:
    @staticmethod
    def serialize(obj_list):
        root = ET.Element("objects")
        for obj in obj_list:
            obj_elem = ET.SubElement(root, "object")

            ET.SubElement(obj_elem, "id").text = str(obj.id)
            ET.SubElement(obj_elem, "name").text = obj.name
            ET.SubElement(obj_elem, "value").text = str(obj.value)
            ET.SubElement(obj_elem, "active").text = str(obj.active)
            ET.SubElement(obj_elem, "score").text = str(obj.score)

            tags_elem = ET.SubElement(obj_elem, "tags")
            for tag in obj.tags:
                ET.SubElement(tags_elem, "tag").text = tag

            metadata_elem = ET.SubElement(obj_elem, "metadata")
            for key, val in obj.metadata.items():
                meta_item = ET.SubElement(metadata_elem, key)
                meta_item.text = str(val)

        # Convert to string with proper formatting
        xml_str = ET.tostring(root, encoding="utf-8", method="xml")
        return xml_str

    @staticmethod
    def deserialize(data, obj_type):
        root = ET.fromstring(data)
        objects = []
        for obj_elem in root.findall("object"):
            obj_dict = {
                "id": int(obj_elem.find("id").text),
                "name": obj_elem.find("name").text,
                "value": float(obj_elem.find("value").text),
                "active": obj_elem.find("active").text.lower() == "true",
                "score": int(obj_elem.find("score").text),
                "tags": [tag.text for tag in obj_elem.find("tags").findall("tag")],
                "metadata": {
                    elem.tag: int(elem.text) if elem.text.isdigit() else elem.text
                    for elem in obj_elem.find("metadata")
                },
            }
            objects.append(obj_type(**obj_dict))
        return objects


class PickleSerializer:
    @staticmethod
    def serialize(obj):
        return pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def deserialize(data, obj_type):
        return pickle.loads(data)


class CompactBinarySerializer:
    """Custom compact binary format using numpy for numeric arrays"""

    @staticmethod
    def serialize(obj_list):
        # Extract arrays for numeric fields
        ids = np.array([obj.id for obj in obj_list], dtype=np.int32)
        values = np.array([obj.value for obj in obj_list], dtype=np.float64)
        scores = np.array([obj.score for obj in obj_list], dtype=np.int32)
        active = np.array([obj.active for obj in obj_list], dtype=np.bool_)

        # Pack everything
        import io

        buffer = io.BytesIO()
        np.save(buffer, ids)
        np.save(buffer, values)
        np.save(buffer, scores)
        np.save(buffer, active)

        # Handle variable-length data (names and tags)
        names = [obj.name.encode("utf-8") for obj in obj_list]
        tags = [",".join(obj.tags).encode("utf-8") for obj in obj_list]

        np.save(buffer, np.array(names, dtype=object))
        np.save(buffer, np.array(tags, dtype=object))

        return buffer.getvalue()

    @staticmethod
    def deserialize(data, obj_type):
        import io

        buffer = io.BytesIO(data)

        ids = np.load(buffer)
        values = np.load(buffer)
        scores = np.load(buffer)
        active = np.load(buffer)
        names = np.load(buffer, allow_pickle=True)
        tags = np.load(buffer, allow_pickle=True)

        objects = []
        for i in range(len(ids)):
            obj = obj_type(
                id=int(ids[i]),
                name=names[i].decode("utf-8"),
                value=float(values[i]),
                active=bool(active[i]),
                tags=tags[i].decode("utf-8").split(","),
                metadata={"created": int(i), "version": "1.0", "score": int(scores[i])},
                score=int(scores[i]),
            )
            objects.append(obj)
        return objects


# ============================================================================
# Main benchmark function
# ============================================================================
def benchmark_formats():
    """Benchmark different serialization formats"""

    N_OBJECTS = 1_000_000  # 1 million objects
    BATCH_SIZE = 100_000  # Process in batches to manage memory

    print("Starting format comparison benchmark")
    print(f"Number of objects: {N_OBJECTS:,}")
    print(f"CSV file: {CSV_FILE}")
    print("=" * 80)

    # Define formats to test
    formats = {
        "msgpack": MessagePackSerializer(),
        "json": JSONSerializer(),
        "json_compact": JSONCompactSerializer(),
        "pickle": PickleSerializer(),
        "xml": XMLSerializer(),  # Too slow for 1M objects, uncomment for smaller tests
        # 'compact_binary': CompactBinarySerializer(),  # Custom format
    }

    # Create test data once (but in batches to manage memory)
    print("\nCreating test data in batches...")

    for format_name, serializer in formats.items():
        print(f"\n{'=' * 60}")
        print(f"Testing {format_name.upper()} format")
        print(f"{'=' * 60}")

        total_serialization_time = 0
        total_deserialization_time = 0
        total_size = 0
        batches = []

        # Track peak memory
        gc.collect()
        start_mem = get_memory_usage()

        # Process in batches
        for batch_start in range(0, N_OBJECTS, BATCH_SIZE):
            batch_end = min(batch_start + BATCH_SIZE, N_OBJECTS)
            batch_size = batch_end - batch_start

            print(
                f"  Batch {batch_start // BATCH_SIZE + 1}: objects {batch_start} to {batch_end}",
                end=" ",
                flush=True,
            )

            # Create batch of objects
            batch = create_test_data(batch_size)

            # Serialization
            start_time = time.time()
            serialized = serializer.serialize(batch)
            serialization_time = time.time() - start_time
            total_serialization_time += serialization_time

            # Deserialization
            start_time = time.time()
            deserialized = serializer.deserialize(serialized, TestData)
            deserialization_time = time.time() - start_time
            total_deserialization_time += deserialization_time

            # Track size
            total_size += len(serialized)

            print(
                f"| Serialized: {serialization_time:.2f}s, Deserialized: {deserialization_time:.2f}s",
                flush=True,
            )

            # Store batch info
            batches.append({"serialized": serialized, "size": len(serialized)})

            # Verify first and last object
            if batch_start == 0:
                assert deserialized[0].id == batch[0].id
                assert deserialized[0].name == batch[0].name
                print("     Ok Verification passed for first object")
            if batch_end == N_OBJECTS:
                assert deserialized[-1].id == batch[-1].id
                assert deserialized[-1].name == batch[-1].name
                print("     Ok Verification passed for last object")

            # Free memory
            del batch
            del deserialized
            gc.collect()

        # Calculate peak memory
        end_mem = get_memory_usage()
        peak_mem = max(end_mem, start_mem)
        mem_used = peak_mem - start_mem

        # Calculate speed
        avg_speed = (total_size / (1024 * 1024)) / total_serialization_time

        # Write results
        write_to_csv(
            format_name=format_name,
            n_objects=N_OBJECTS,
            serialization_time=total_serialization_time,
            deserialization_time=total_deserialization_time,
            serialized_size_mb=total_size / (1024 * 1024),
            mem_usage_mb=mem_used,
            speed_mb_per_sec=avg_speed,
        )

        print(f"\n  Summary for {format_name}:")
        print(f"    Total serialization: {total_serialization_time:.2f}s")
        print(f"    Total deserialization: {total_deserialization_time:.2f}s")
        print(f"    Total size: {total_size / (1024 * 1024):.2f} MB")
        print(f"    Avg speed: {avg_speed:.2f} MB/s")
        print(f"    Memory usage: {mem_used:.2f} MB")

        # Clean up batches
        del batches
        gc.collect()


# ============================================================================
# Detailed analysis with different object sizes
# ============================================================================
def benchmark_with_different_sizes():
    """Test formats with different numbers of objects to see scaling"""

    object_counts = [1000, 10000, 100000, 500000, 1000000]
    formats = {
        "msgpack": MessagePackSerializer(),
        "json": JSONSerializer(),
        "json_compact": JSONCompactSerializer(),
        "pickle": PickleSerializer(),
    }

    print("\n" + "=" * 80)
    print("SCALING BENCHMARK: Testing with different object counts")
    print("=" * 80)

    for n_objects in object_counts:
        print(f"\n--- Testing with {n_objects:,} objects ---")

        for format_name, serializer in formats.items():
            # Create objects
            objects = create_test_data(n_objects)

            # Serialization
            gc.collect()
            start_mem = get_memory_usage()
            start_time = time.time()
            serialized = serializer.serialize(objects)
            serialization_time = time.time() - start_time

            # Deserialization
            start_time = time.time()
            deserialized = serializer.deserialize(serialized, TestData)
            deserialization_time = time.time() - start_time

            end_mem = get_memory_usage()
            mem_used = end_mem - start_mem

            # Verify
            assert len(deserialized) == n_objects
            assert deserialized[0].id == objects[0].id

            print(
                f"  {format_name:15} | Serialize: {serialization_time:6.2f}s | "
                f"Deserialize: {deserialization_time:6.2f}s | "
                f"Size: {len(serialized) / (1024 * 1024):6.2f}MB | "
                f"Mem: {mem_used:6.2f}MB"
            )

            del objects, serialized, deserialized
            gc.collect()


if __name__ == "__main__":
    print("MSGPEC Format Comparison Benchmark")
    print("Testing serialization performance across different formats")
    print("=" * 80)

    # Check if psutil is installed
    try:
        import psutil
    except ImportError:
        print("ERROR: psutil is required. Install with: pip install psutil")
        exit(1)

    try:
        # Run main benchmark
        benchmark_formats()

        # Run scaling benchmark
        benchmark_with_different_sizes()

        print("\n" + "=" * 80)
        print(f"Benchmark completed! Results saved to {CSV_FILE}")

        # Show results
        print("\nResults summary:")
        with open(CSV_FILE, "r") as f:
            lines = f.readlines()
            print(lines[0].strip())
            for line in lines[1:11]:  # Show first 10 results
                print(line.strip())

    except KeyboardInterrupt:
        print("\n\nBenchmark interrupted by user")
    except Exception as e:
        print(f"\nError occurred: {e}")
        import traceback

        traceback.print_exc()
        raise
