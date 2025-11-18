"""
Common utilities for research projects
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any

def setup_research_logging(project_name: str) -> logging.Logger:
    """Set up logging for a research project"""
    logging.basicConfig(
        level=logging.INFO,
        format=f'%(asctime)s - {project_name} - %(levelname)s - %(message)s'
    )
    return logging.getLogger(project_name)

def save_research_data(data: Dict[str, Any], filepath: Path) -> None:
    """Save research data to JSON file"""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_research_data(filepath: Path) -> Dict[str, Any]:
    """Load research data from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)