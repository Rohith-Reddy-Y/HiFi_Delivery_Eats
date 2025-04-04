#!/usr/bin/env bash
# Custom Render build script

echo "📦 Upgrading pip..."
pip install --upgrade pip

echo "📦 Installing requirements..."
pip install -r requirements.txt
