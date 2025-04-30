#!/usr/bin/env python3
"""
Run Script

This script provides a convenient way to run the different components of the
restaurant chatbot system.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def run_scraper(args):
    """Run the web scraper."""
    print("Running web scraper...")
    
    cmd = ["python", "src/scraper/main.py"]
    
    if args.restaurant:
        cmd.extend(["--restaurant", args.restaurant])
    
    if args.mock:
        cmd.append("--mock")
    
    subprocess.run(cmd)

def build_knowledge_base(args):
    """Build the knowledge base."""
    print("Building knowledge base...")
    
    cmd = ["python", "src/knowledge_base/build_kb.py"]
    
    if args.process:
        cmd.append("--process")
    
    if args.model:
        cmd.extend(["--model", args.model])
    
    subprocess.run(cmd)

def run_app(args):
    """Run the Streamlit app."""
    print("Running Streamlit app...")
    
    cmd = ["streamlit", "run", "src/app.py"]
    
    subprocess.run(cmd)

def run_pipeline(args):
    """Run the entire pipeline."""
    print("Running the entire pipeline...")
    
    # First, run the scraper
    scraper_args = argparse.Namespace()
    scraper_args.restaurant = args.restaurant
    scraper_args.mock = args.mock
    run_scraper(scraper_args)
    
    # Then, build the knowledge base
    kb_args = argparse.Namespace()
    kb_args.process = True
    kb_args.model = args.model
    build_knowledge_base(kb_args)
    
    # Finally, run the app
    run_app(argparse.Namespace())

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run the restaurant chatbot system.")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Scraper command
    scraper_parser = subparsers.add_parser("scrape", help="Run the web scraper")
    scraper_parser.add_argument("--restaurant", type=str, help="Scrape a specific restaurant")
    scraper_parser.add_argument("--mock", action="store_true", help="Use mock data")
    
    # Knowledge base command
    kb_parser = subparsers.add_parser("build_kb", help="Build the knowledge base")
    kb_parser.add_argument("--process", action="store_true", help="Process raw data before building")
    kb_parser.add_argument("--model", type=str, default="sentence-transformers/all-MiniLM-L6-v2", help="Model to use for embeddings")
    
    # App command
    app_parser = subparsers.add_parser("app", help="Run the Streamlit app")
    
    # Pipeline command
    pipeline_parser = subparsers.add_parser("pipeline", help="Run the entire pipeline")
    pipeline_parser.add_argument("--restaurant", type=str, help="Scrape a specific restaurant")
    pipeline_parser.add_argument("--mock", action="store_true", help="Use mock data")
    pipeline_parser.add_argument("--model", type=str, default="sentence-transformers/all-MiniLM-L6-v2", help="Model to use for embeddings")
    
    args = parser.parse_args()
    
    # Create data directories if they don't exist
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    
    # Execute the appropriate command
    if args.command == "scrape":
        run_scraper(args)
    elif args.command == "build_kb":
        build_knowledge_base(args)
    elif args.command == "app":
        run_app(args)
    elif args.command == "pipeline":
        run_pipeline(args)
    else:
        # If no command is provided, show help
        parser.print_help()

if __name__ == "__main__":
    main() 