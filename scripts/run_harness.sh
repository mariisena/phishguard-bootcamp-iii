#!/bin/bash
set -euo pipefail

mkdir -p logs
LOGFILE="logs/harness_$(date +%Y%m%d_%H%M%S).log"

echo "Running test harness..."

# Usa pytest se disponível no PATH, senão faz fallback para python -m pytest
if command -v pytest >/dev/null 2>&1; then
    PYTEST_CMD="pytest"
elif command -v python >/dev/null 2>&1; then
    PYTEST_CMD="python -m pytest"
elif command -v python.exe >/dev/null 2>&1; then
    PYTEST_CMD="python.exe -m pytest"
else
    echo "Error: pytest not found. Please install pytest or activate your virtual environment."
    exit 1
fi

# A opção pipefail está ativa, mas capturamos o exit code manualmente 
# do array PIPESTATUS para exibir um resumo correto no final sem interromper a execução prematuramente.
set +e
$PYTEST_CMD -v | tee "$LOGFILE"
EXIT_CODE=${PIPESTATUS[0]}
set -e

echo ""
if [ "$EXIT_CODE" -eq 0 ]; then
    echo "✅ Tests passed! Log saved to: $LOGFILE"
else
    echo "❌ Tests failed with exit code $EXIT_CODE. Log saved to: $LOGFILE"
fi

# Propaga o exit code original do pytest
exit "$EXIT_CODE"