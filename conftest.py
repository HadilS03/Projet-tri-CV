"""Configuration commune des tests : rend les paquets core/ et frontend/ importables."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
