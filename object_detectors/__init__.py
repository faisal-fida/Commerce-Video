"""
object_detectors package initialization.
"""

from .clothing_detector import ClothingDetector
from .jewelry_detector import JewelryDetector
from .person_detector import PersonDetector

__all__ = ["ClothingDetector", "JewelryDetector", "PersonDetector"]
