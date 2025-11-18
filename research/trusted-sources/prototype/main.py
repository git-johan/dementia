#!/usr/bin/env python3
"""
Main CLI interface for trusted sources research prototype
"""
import argparse
import json
import logging
from pathlib import Path

from .config import TrustedSourcesConfig
from .storage import TrustedSourcesStorage
from .collector import ContentCollector
from .processor import ContentProcessor


def setup_logging(level: str = "INFO"):
    """Set up logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def cmd_collect(args):
    """Handle collect command"""
    config = TrustedSourcesConfig()
    storage = TrustedSourcesStorage()
    collector = ContentCollector(config, storage)

    if args.domain:
        if not config.is_trusted_domain(args.domain):
            print(f"Error: {args.domain} is not a trusted domain")
            print("Available domains:")
            for domain in config.get_all_sources().keys():
                print(f"  - {domain}")
            return

        result = collector.collect_from_domain(args.domain, args.max_pages)
        print(f"Collection completed for {args.domain}")
        print(f"Status: {result['status']}")
        print(f"Pages collected: {result.get('pages_collected', 0)}")

    elif args.priority:
        domains = config.get_sources_by_priority(args.priority)
        if not domains:
            print(f"No domains found with priority '{args.priority}'")
            print("Available priorities: high, medium, low")
            return

        print(f"Collecting from {len(domains)} domains with priority '{args.priority}'")
        for domain in domains.keys():
            print(f"\nCollecting from {domain}...")
            try:
                result = collector.collect_from_domain(domain, args.max_pages)
                print(f"  Status: {result['status']}")
                print(f"  Pages collected: {result.get('pages_collected', 0)}")
            except Exception as e:
                print(f"  Error: {e}")

    else:
        print("Error: Must specify either --domain or --priority")


def cmd_analyze(args):
    """Handle analyze command"""
    storage = TrustedSourcesStorage()
    processor = ContentProcessor(storage)

    if args.content_type == "quality":
        analysis = processor.analyze_content_quality(args.domain)
        print("Content Quality Analysis:")
        print(json.dumps(analysis, indent=2))

    elif args.content_type == "duplicates":
        duplicates = processor.find_duplicates(args.similarity_threshold)
        print(f"Found {len(duplicates)} duplicate pairs:")
        for dup in duplicates:
            print(f"  Similarity: {dup['similarity']:.3f}")
            print(f"    {dup['content1_domain']}: {dup['content1_url']}")
            print(f"    {dup['content2_domain']}: {dup['content2_url']}")
            print()

    elif args.content_type == "stats":
        stats = storage.get_collection_stats()
        print("Collection Statistics:")
        print(json.dumps(stats, indent=2))

    else:
        print("Error: Invalid content type. Use 'quality', 'duplicates', or 'stats'")


def cmd_extract(args):
    """Handle extract command"""
    storage = TrustedSourcesStorage()
    processor = ContentProcessor(storage)

    if args.content_id:
        info = processor.extract_key_information(args.content_id)
        print("Extracted Information:")
        print(json.dumps(info, indent=2, ensure_ascii=False))

        # Generate citation
        citation = processor.generate_citation(args.content_id)
        print(f"\nCitation:")
        print(citation)

    else:
        print("Error: Must specify --content-id")


def cmd_export(args):
    """Handle export command"""
    storage = TrustedSourcesStorage()

    try:
        exported_data = storage.export_content(args.format, args.min_quality)

        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(exported_data)
            print(f"Data exported to {output_path}")
        else:
            print(exported_data)

    except Exception as e:
        print(f"Export failed: {e}")


def cmd_status(args):
    """Handle status command"""
    config = TrustedSourcesConfig()
    storage = TrustedSourcesStorage()

    print("Trusted Sources Research Status\n")

    # Show configuration
    print("Configured Sources:")
    norwegian_sources = config.get_norwegian_sources()
    for domain, conf in norwegian_sources.items():
        print(f"  🇳🇴 {domain} ({conf['priority']} priority)")

    international_sources = config.get_international_sources()
    for domain, conf in international_sources.items():
        print(f"  🌍 {domain} ({conf['priority']} priority)")

    print()

    # Show collection statistics
    stats = storage.get_collection_stats()
    print("Collection Statistics:")
    print(f"  Total content: {stats['total_content']}")
    print(f"  High quality: {stats['quality_distribution']['high_quality']}")
    print(f"  Medium quality: {stats['quality_distribution']['medium_quality']}")
    print(f"  Low quality: {stats['quality_distribution']['low_quality']}")

    print("\nContent by Domain:")
    for domain, count in stats['content_by_domain'].items():
        print(f"  {domain}: {count} articles")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Trusted Sources Research Prototype")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Collect command
    collect_parser = subparsers.add_parser("collect", help="Collect content from trusted sources")
    collect_parser.add_argument("--domain", help="Specific domain to collect from")
    collect_parser.add_argument("--priority", choices=["high", "medium", "low"],
                              help="Collect from all domains of specified priority")
    collect_parser.add_argument("--max-pages", type=int, help="Maximum pages to collect")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze collected content")
    analyze_parser.add_argument("--content-type", required=True,
                               choices=["quality", "duplicates", "stats"],
                               help="Type of analysis to perform")
    analyze_parser.add_argument("--domain", help="Analyze specific domain only")
    analyze_parser.add_argument("--similarity-threshold", type=float, default=0.8,
                               help="Similarity threshold for duplicate detection")

    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract information from specific content")
    extract_parser.add_argument("--content-id", type=int, required=True,
                               help="ID of content to extract information from")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export collected data")
    export_parser.add_argument("--format", default="json", choices=["json"],
                              help="Export format")
    export_parser.add_argument("--min-quality", type=float, default=0.0,
                              help="Minimum quality threshold for export")
    export_parser.add_argument("--output", help="Output file path")

    # Status command
    status_parser = subparsers.add_parser("status", help="Show research project status")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    setup_logging(args.log_level)

    # Route to appropriate command handler
    command_handlers = {
        "collect": cmd_collect,
        "analyze": cmd_analyze,
        "extract": cmd_extract,
        "export": cmd_export,
        "status": cmd_status
    }

    handler = command_handlers.get(args.command)
    if handler:
        try:
            handler(args)
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
        except Exception as e:
            print(f"Error: {e}")
            if args.log_level == "DEBUG":
                import traceback
                traceback.print_exc()
    else:
        print(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()