param(
    [int]$Runs = 1
)

if ($Runs -lt 1) {
    Write-Host "Количество запусков должно быть больше 0"
    exit 1
}

for ($i = 1; $i -le $Runs; $i++) {

    Write-Host ""
    Write-Host "========================================="
    Write-Host "#$i/$Runs"
    Write-Host "========================================="
    Write-Host ""

    Write-Host "[1/4] benchmark_creation.py"
    uv run benchmarks/benchmark_creation.py

    Write-Host ""
    Write-Host "[2/4] benchmark_memory.py"
    uv run benchmarks/benchmark_memory.py

    Write-Host ""
    Write-Host "[3/4] benchmark_serialization.py"
    uv run benchmarks/benchmark_serialization.py

    Write-Host ""
    Write-Host "[4/4] benchmark_real_cases.py"
    uv run benchmarks/benchmark_real_cases.py
}