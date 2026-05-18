import msgspec
import pydantic
import time
import os
import csv
from dataclasses import dataclass, field
from typing import Dict
import psutil
import gc

# Create results directory if it doesn't exist
os.makedirs("results", exist_ok=True)

# CSV file setup
CSV_FILE = "results/continuous_serialization.csv"
csv_headers = ["m_name", "n_args", "t_creation", "t_serialization", "mem"]

# Initialize CSV file with headers
with open(CSV_FILE, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=csv_headers)
    writer.writeheader()


# MSGSPEC implementation
class MsgspecData(msgspec.Struct):
    extra: Dict[str, int] = {}

    def __repr__(self):
        return f"MsgspecData({self.extra})"


# PYDANTIC implementation
class PydanticData(pydantic.BaseModel):
    extra: Dict[str, int] = {}

    class Config:
        arbitrary_types_allowed = True

    def __repr__(self):
        return f"PydanticData({self.extra})"


# DATACLASS implementation
@dataclass
class DataclassData:
    extra: Dict[str, int] = field(default_factory=dict)

    def __repr__(self):
        return f"DataclassData({self.extra})"


def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process()
    return process.memory_info().rss / (1024 * 1024)


def write_to_csv(m_name, n_args, t_creation, t_serialization, mem):
    """Write a single row to CSV file"""
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_headers)
        writer.writerow(
            {
                "m_name": m_name,
                "n_args": n_args,
                "t_creation": round(t_creation, 4),
                "t_serialization": round(t_serialization, 4),
                "mem": round(mem, 2),
            }
        )


def generate_objects():
    """Generate objects with progressively more arguments using all three libraries"""

    START_FIELDS = 1
    END_FIELDS = 100
    OBJECTS_PER_STEP = 100_000

    print("Starting benchmark...")
    print(f"CSV file: {CSV_FILE}")
    print(f"Fields: {START_FIELDS} to {END_FIELDS}")
    print(f"Objects per step: {OBJECTS_PER_STEP:,}")
    print("-" * 60)

    # Encoders for each library
    msgspec_encoder = msgspec.msgpack.Encoder()
    pydantic_encoder = pydantic.TypeAdapter(list[PydanticData])

    for num_fields in range(START_FIELDS, END_FIELDS + 1):
        print(f"\nProcessing {num_fields} fields...", end=" ", flush=True)

        # MSGSPEC
        gc.collect()  # Force garbage collection before memory measurement
        mem_before = get_memory_usage()
        start_time = time.time()

        msgspec_batch = []
        for obj_id in range(OBJECTS_PER_STEP):
            kwargs = {}
            for i in range(num_fields):
                kwargs[f"field_{i + 1}"] = obj_id + i + 1
            obj = MsgspecData(extra=kwargs)
            msgspec_batch.append(obj)

        creation_time = time.time()
        t_creation = creation_time - start_time

        serialized = msgspec_encoder.encode(msgspec_batch)
        serialization_time = time.time()
        t_serialization = serialization_time - creation_time

        mem_after = get_memory_usage()
        mem_used = mem_after - mem_before

        # Write to CSV
        write_to_csv("msgspec", num_fields, t_creation, t_serialization, mem_used)
        print("MS done", end=" ", flush=True)

        # Free memory
        del msgspec_batch
        del serialized

        # PYDANTIC
        gc.collect()
        mem_before = get_memory_usage()
        start_time = time.time()

        pydantic_batch = []
        for obj_id in range(OBJECTS_PER_STEP):
            kwargs = {}
            for i in range(num_fields):
                kwargs[f"field_{i + 1}"] = obj_id + i + 1
            obj = PydanticData(extra=kwargs)
            pydantic_batch.append(obj)

        creation_time = time.time()
        t_creation = creation_time - start_time

        serialized = pydantic_encoder.dump_json(pydantic_batch)
        serialization_time = time.time()
        t_serialization = serialization_time - creation_time

        mem_after = get_memory_usage()
        mem_used = mem_after - mem_before

        # Write to CSV
        write_to_csv("pydantic", num_fields, t_creation, t_serialization, mem_used)
        print("PD done", end=" ", flush=True)

        # Free memory
        del pydantic_batch
        del serialized

        # DATACLASS
        gc.collect()
        mem_before = get_memory_usage()
        start_time = time.time()

        dataclass_batch = []
        for obj_id in range(OBJECTS_PER_STEP):
            kwargs = {}
            for i in range(num_fields):
                kwargs[f"field_{i + 1}"] = obj_id + i + 1
            obj = DataclassData(extra=kwargs)
            dataclass_batch.append(obj)

        creation_time = time.time()
        t_creation = creation_time - start_time

        serialized = msgspec_encoder.encode(dataclass_batch)
        serialization_time = time.time()
        t_serialization = serialization_time - creation_time

        mem_after = get_memory_usage()
        mem_used = mem_after - mem_before

        # Write to CSV
        write_to_csv("dataclass", num_fields, t_creation, t_serialization, mem_used)
        print("DC done", end=" ", flush=True)

        # Free memory
        del dataclass_batch
        del serialized

        # Progress update
        if num_fields % 100 == 0:
            print(
                f"\n  Progress: {num_fields}/{END_FIELDS} field configurations completed"
            )


if __name__ == "__main__":
    print("Starting progressive serialization with msgspec, pydantic, and dataclass")
    print(f"Results will be saved to {CSV_FILE}")
    print("=" * 60)

    # Check if psutil is installed
    try:
        import psutil
    except ImportError:
        print("ERROR: psutil is required. Install with: pip install psutil")
        exit(1)

    try:
        generate_objects()
        print("\n" + "=" * 60)
        print(f"Benchmark completed! Results saved to {CSV_FILE}")

        # Show first few lines of CSV
        print("\nFirst few rows of CSV:")
        with open(CSV_FILE, "r") as f:
            for i, line in enumerate(f):
                if i < 10:
                    print(f"  {line.strip()}")
                else:
                    break

    except KeyboardInterrupt:
        print("\n\nBenchmark interrupted by user")
    except Exception as e:
        print(f"\nError occurred: {e}")
        raise
