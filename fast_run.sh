#!/bin/bash

RUNS=${1:-1}

if [ "$RUNS" -lt 1 ]; then
    echo "Количество запусков должно быть больше 0"
    exit 1
fi

for ((i=1; i<=RUNS; i++))
do
    echo ""
    echo "========================================="
    echo "Запуск #$i"
    echo "========================================="
    echo ""

    echo "[1/4] benchmark_creation.py"
    uv run benchmarks/benchmark_creation.py

    echo ""
    echo "[2/4] benchmark_memory.py"
    uv run benchmarks/benchmark_memory.py

    echo ""
    echo "[3/4] benchmark_serialization.py"
    uv run benchmarks/benchmark_serialization.py

    echo ""
    echo "[4/4] benchmark_real_cases.py"
    uv run benchmarks/benchmark_real_cases.py

    echo ""
    echo "Запуск #$i завершён"
    echo ""
done