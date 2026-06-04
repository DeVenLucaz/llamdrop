"""
Tests for prompt building in modules/chat.py
"""
import unittest
import sys
import os

# Add modules to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'modules')))

from chat import _build_prompt, _extract_response

class TestPrompts(unittest.TestCase):
    
    def test_build_chatml(self):
        history = [{"role": "user", "content": "Hello"}]
        system = "You are AI"
        prompt = _build_prompt(history, system, "chatml")
        self.assertIn("<|im_start|>system\nYou are AI<|im_end|>", prompt)
        self.assertIn("<|im_start|>user\nHello<|im_end|>", prompt)
        self.assertIn("<|im_start|>assistant", prompt)

    def test_build_llama3(self):
        history = [{"role": "user", "content": "Hello"}]
        system = "You are AI"
        prompt = _build_prompt(history, system, "llama3")
        self.assertIn("<|start_header_id|>system<|end_header_id|>\n\nYou are AI<|eot_id|>", prompt)
        self.assertIn("<|start_header_id|>user<|end_header_id|>\n\nHello<|eot_id|>", prompt)
        self.assertIn("<|start_header_id|>assistant<|end_header_id|>", prompt)

    def test_extract_response(self):
        raw = "Some noise\n<|im_start|>assistant\nHello there!\n<|im_end|>\n[ Prompt: 1.2 t/s ]"
        clean = _extract_response(raw)
        self.assertEqual(clean, "Hello there!")

if __name__ == '__main__':
    unittest.main()
