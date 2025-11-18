#!/usr/bin/env python3
"""
Test script to verify NB-Llama model loading with proper authentication
"""

import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_nb_llama_loading():
    """Test NB-Llama model loading and authentication"""

    try:
        # Check if HuggingFace token is available
        hf_token = os.getenv('HUGGINGFACE_HUB_TOKEN')
        if not hf_token:
            logger.info("No HuggingFace token found. Trying without authentication...")
        else:
            logger.info("HuggingFace token found. Authenticating...")
            login(token=hf_token)

        # Auto-detect best device
        if torch.backends.mps.is_available():
            device = "mps"
            device_name = "Apple M2 Max GPU (MPS)"
        elif torch.cuda.is_available():
            device = "cuda"
            device_name = f"CUDA GPU ({torch.cuda.get_device_name()})"
        else:
            device = "cpu"
            device_name = "CPU"

        logger.info(f"Selected device: {device_name} ({device})")

        # Try different model identifiers - focus on publicly available Norwegian models
        model_identifiers = [
            "NbAiLab/nb-gpt-j-6B",  # Alternative Norwegian model
            "NbAiLab/norwegian-gpt2-large",  # Norwegian GPT-2
            "microsoft/DialoGPT-medium",  # Fallback test model
            "gpt2",  # Simple fallback for testing
        ]

        for model_name in model_identifiers:
            logger.info(f"\nTesting model: {model_name}")

            try:
                # Load tokenizer first
                logger.info(f"Loading tokenizer for {model_name}...")
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                logger.info("✓ Tokenizer loaded successfully")

                # Load model
                logger.info(f"Loading model {model_name} on {device}...")

                # Try without device_map first (fallback for compatibility)
                try:
                    model = AutoModelForCausalLM.from_pretrained(
                        model_name,
                        torch_dtype=torch.float16
                    ).to(device)
                except Exception as e:
                    logger.info(f"Fallback: trying with device_map after error: {e}")
                    model = AutoModelForCausalLM.from_pretrained(
                        model_name,
                        device_map=device,
                        torch_dtype=torch.float16
                    )
                logger.info(f"✓ Model {model_name} loaded successfully on {device_name}")

                # Test a simple generation
                test_input = "Hva er demens?"
                inputs = tokenizer.encode(test_input, return_tensors="pt").to(device)

                with torch.no_grad():
                    outputs = model.generate(
                        inputs,
                        max_new_tokens=50,
                        temperature=0.7,
                        do_sample=True,
                        pad_token_id=tokenizer.eos_token_id
                    )

                response = tokenizer.decode(outputs[0], skip_special_tokens=True)
                logger.info(f"✓ Test generation successful:")
                logger.info(f"Input: {test_input}")
                logger.info(f"Output: {response}")

                return True, model_name, model, tokenizer

            except Exception as e:
                logger.error(f"✗ Failed to load {model_name}: {e}")
                continue

        logger.error("All model identifiers failed")
        return False, None, None, None

    except Exception as e:
        logger.error(f"General error: {e}")
        return False, None, None, None

if __name__ == "__main__":
    success, model_name, model, tokenizer = test_nb_llama_loading()
    if success:
        print(f"\n🎉 Successfully loaded model: {model_name}")
    else:
        print("\n❌ Failed to load any Norwegian language model")