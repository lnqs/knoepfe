#!/usr/bin/env bash
set -e

echo "Running core tests..."
uv run pytest tests/ -v

echo -e "\nRunning audio plugin tests..."
pushd plugins/audio
uv run pytest tests/ -v
popd

echo -e "\nRunning example plugin tests..."
pushd plugins/example
uv run pytest tests/ -v
popd

echo -e "\nRunning OBS plugin tests..."
pushd plugins/obs
uv run pytest tests/ -v
popd

echo -e "\nAll tests passed!"