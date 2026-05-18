import msgspec
import pydantic
import time
import os
import csv
from dataclasses import dataclass
from typing import Optional, List
import psutil
import gc

# Create results directory if it doesn't exist
os.makedirs("results", exist_ok=True)

# CSV file setup
CSV_FILE = "results/nested_serialization.csv"
csv_headers = [
    "m_name",
    "depth",
    "t_creation",
    "t_serialization",
    "t_deserialization",
    "mem",
    "serialized_size",
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
    m_name, depth, t_creation, t_serialization, t_deserialization, mem, serialized_size
):
    """Write a single row to CSV file"""
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_headers)
        writer.writerow(
            {
                "m_name": m_name,
                "depth": depth,
                "t_creation": round(t_creation, 4),
                "t_serialization": round(t_serialization, 4),
                "t_deserialization": round(t_deserialization, 4),
                "mem": round(mem, 2),
                "serialized_size": round(
                    serialized_size / (1024 * 1024), 2
                ),  # Convert to MB
            }
        )


# ============================================================================
# MSGSPEC Implementation with nested structure
# ============================================================================
class MsgspecNode(msgspec.Struct):
    value: int
    child: Optional["MsgspecNode"] = None


# ============================================================================
# PYDANTIC Implementation with nested structure
# ============================================================================
class PydanticNode(pydantic.BaseModel):
    value: int
    child: Optional["PydanticNode"] = None

    class Config:
        arbitrary_types_allowed = True


# Update forward reference
PydanticNode.model_rebuild()


# ============================================================================
# DATACLASS Implementation with nested structure
# ============================================================================
@dataclass
class DataclassNode:
    value: int
    child: Optional["DataclassNode"] = None


def create_nested_object(depth: int, library: str):
    """Create a nested object of specified depth"""
    if library == "msgspec":
        # Create from deepest to shallowest
        current = None
        for i in range(depth, 0, -1):
            current = MsgspecNode(value=i, child=current)
        return current

    elif library == "pydantic":
        current = None
        for i in range(depth, 0, -1):
            current = PydanticNode(value=i, child=current)
        return current

    elif library == "dataclass":
        current = None
        for i in range(depth, 0, -1):
            current = DataclassNode(value=i, child=current)
        return current

    else:
        raise ValueError(f"Unknown library: {library}")


def verify_nested_depth(obj, library: str, expected_depth: int):
    """Verify the nested object has the expected depth"""
    depth = 0
    current = obj
    while current is not None:
        depth += 1
        if library == "msgspec":
            current = current.child
        elif library == "pydantic":
            current = current.child
        elif library == "dataclass":
            current = current.child
    return depth == expected_depth


def generate_nested_objects():
    """Generate nested objects with increasing depth"""

    START_DEPTH = 1
    END_DEPTH = 98  # Up to 98 levels of nesting
    OBJECTS_PER_STEP = 1000  # Number of objects per depth level

    print("Starting nested object benchmark...")
    print(f"CSV file: {CSV_FILE}")
    print(f"Depth range: {START_DEPTH} to {END_DEPTH}")
    print(f"Objects per depth: {OBJECTS_PER_STEP:,}")
    print("-" * 60)

    # Encoders and decoders for lists
    msgspec_encoder = msgspec.msgpack.Encoder()
    # Decoder for list of MsgspecNode
    msgspec_decoder = msgspec.msgpack.Decoder(List[MsgspecNode])

    pydantic_encoder = pydantic.TypeAdapter(List[PydanticNode])
    pydantic_decoder = pydantic.TypeAdapter(List[PydanticNode])

    # Decoder for list of DataclassNode
    msgspec_dataclass_decoder = msgspec.msgpack.Decoder(List[DataclassNode])

    for depth in range(START_DEPTH, END_DEPTH + 1):
        print(f"\nProcessing depth {depth}...", end=" ", flush=True)

        # ====================================================================
        # MSGSPEC
        # ====================================================================
        gc.collect()
        mem_before = get_memory_usage()
        start_time = time.time()

        msgspec_objects = []
        for obj_id in range(OBJECTS_PER_STEP):
            obj = create_nested_object(depth, "msgspec")
            msgspec_objects.append(obj)

        creation_time = time.time()
        t_creation = creation_time - start_time

        # Serialize
        serialized = msgspec_encoder.encode(msgspec_objects)
        serialization_time = time.time()
        t_serialization = serialization_time - creation_time

        # Deserialize - decode as list of MsgspecNode
        deserialized = msgspec_decoder.decode(serialized)
        deserialization_time = time.time()
        t_deserialization = deserialization_time - serialization_time

        # Verify depth of first object
        if verify_nested_depth(msgspec_objects[0], "msgspec", depth):
            verified = "Ok"
        else:
            verified = "X"

        mem_after = get_memory_usage()
        mem_used = mem_after - mem_before
        serialized_size = len(serialized)

        write_to_csv(
            "msgspec",
            depth,
            t_creation,
            t_serialization,
            t_deserialization,
            mem_used,
            serialized_size,
        )
        print(f"MS{verified} done", end=" ", flush=True)

        # Free memory
        del msgspec_objects
        del serialized
        del deserialized

        # ====================================================================
        # PYDANTIC
        # ====================================================================
        gc.collect()
        mem_before = get_memory_usage()
        start_time = time.time()

        pydantic_objects = []
        for obj_id in range(OBJECTS_PER_STEP):
            obj = create_nested_object(depth, "pydantic")
            pydantic_objects.append(obj)

        creation_time = time.time()
        t_creation = creation_time - start_time

        # Serialize (using dump_json for bytes output)
        serialized = pydantic_encoder.dump_json(pydantic_objects)
        serialization_time = time.time()
        t_serialization = serialization_time - creation_time

        # Deserialize
        deserialized = pydantic_decoder.validate_json(serialized)
        deserialization_time = time.time()
        t_deserialization = deserialization_time - serialization_time

        # Verify depth
        if verify_nested_depth(pydantic_objects[0], "pydantic", depth):
            verified = "Ok"
        else:
            verified = "X"

        mem_after = get_memory_usage()
        mem_used = mem_after - mem_before
        serialized_size = len(serialized)

        write_to_csv(
            "pydantic",
            depth,
            t_creation,
            t_serialization,
            t_deserialization,
            mem_used,
            serialized_size,
        )
        print(f"PD{verified} done", end=" ", flush=True)

        # Free memory
        del pydantic_objects
        del serialized
        del deserialized

        # ====================================================================
        # DATACLASS
        # ====================================================================
        gc.collect()
        mem_before = get_memory_usage()
        start_time = time.time()

        dataclass_objects = []
        for obj_id in range(OBJECTS_PER_STEP):
            obj = create_nested_object(depth, "dataclass")
            dataclass_objects.append(obj)

        creation_time = time.time()
        t_creation = creation_time - start_time

        # Serialize using msgspec
        serialized = msgspec_encoder.encode(dataclass_objects)
        serialization_time = time.time()
        t_serialization = serialization_time - creation_time

        # Deserialize - decode as list of DataclassNode
        deserialized = msgspec_dataclass_decoder.decode(serialized)
        deserialization_time = time.time()
        t_deserialization = deserialization_time - serialization_time

        # Verify depth
        if verify_nested_depth(dataclass_objects[0], "dataclass", depth):
            verified = "Ok"
        else:
            verified = "X"

        mem_after = get_memory_usage()
        mem_used = mem_after - mem_before
        serialized_size = len(serialized)

        write_to_csv(
            "dataclass",
            depth,
            t_creation,
            t_serialization,
            t_deserialization,
            mem_used,
            serialized_size,
        )
        print(f"DC{verified} done", end=" ", flush=True)

        # Free memory
        del dataclass_objects
        del serialized
        del deserialized

        # Progress update
        if depth % 10 == 0:
            print(f"\n  Progress: {depth}/{END_DEPTH} depth levels completed")


if __name__ == "__main__":
    print("Starting nested object serialization benchmark")
    print("Testing msgspec, pydantic, and dataclass with nested structures")
    print("=" * 60)

    # Check if psutil is installed
    try:
        import psutil
    except ImportError:
        print("ERROR: psutil is required. Install with: pip install psutil")
        exit(1)

    try:
        generate_nested_objects()
        print("\n" + "=" * 60)
        print(f"Benchmark completed! Results saved to {CSV_FILE}")

        # Show first few rows of CSV
        print("\nFirst few rows of CSV:")
        with open(CSV_FILE, "r") as f:
            for i, line in enumerate(f):
                if i < 10:
                    print(f"  {line.strip()}")
                else:
                    break

    except KeyboardInterrupt:
        print("\n\nBenchmark interrupted by user")
    except RecursionError:
        print("\n\nERROR: Recursion depth exceeded. Try reducing END_DEPTH")
        print("Python has a default recursion limit. For deeper nesting, use:")
        print("  import sys; sys.setrecursionlimit(10000)")
    except Exception as e:
        print(f"\nError occurred: {e}")
        import traceback

        traceback.print_exc()
        raise
