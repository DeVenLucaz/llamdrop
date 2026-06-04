"""
Tests for modules/specs.py
"""
import unittest
import sys
import os

# Add modules to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'modules')))

from specs import classify_tier, Tier, select_threads, select_ctx_size

class TestSpecs(unittest.TestCase):
    
    def test_classify_tier(self):
        self.assertEqual(classify_tier(1.5), Tier.MICRO)
        self.assertEqual(classify_tier(3.5), Tier.LOW)
        self.assertEqual(classify_tier(5.0), Tier.LOW_MID)
        self.assertEqual(classify_tier(10.0), Tier.MID)
        self.assertEqual(classify_tier(20.0), Tier.HIGH)
        self.assertEqual(classify_tier(40.0), Tier.DESKTOP)
        self.assertEqual(classify_tier(128.0), Tier.WORKSTATION)

    def test_select_threads(self):
        # x86 physical cores cap at 16
        self.assertEqual(select_threads("x86_64", 32, 0, "Intel"), 16)
        self.assertEqual(select_threads("x86_64", 8, 0, "Intel"), 8)
        
        # ARM big.LITTLE
        self.assertEqual(select_threads("aarch64", 8, 4, "Snapdragon"), 4)
        
        # Fallback half
        self.assertEqual(select_threads("unknown", 4, 0, "Unknown"), 2)

    def test_select_ctx_size(self):
        self.assertEqual(select_ctx_size(Tier.MICRO), 512)
        self.assertEqual(select_ctx_size(Tier.WORKSTATION), 16384)

if __name__ == '__main__':
    unittest.main()
