from typing import Dict, List, Type, Optional, Any
import asyncio
import logging
from .base import MemoryProcessor, ProcessorResult, ProcessorCapabilities

logger = logging.getLogger(__name__)


class ProcessorRegistry:
    """Registry for managing processor plugins.

    This implements our processor plugin pattern where different input types
    (speech, documents, photos) can be added as plugins without changing
    the core API.
    """

    def __init__(self):
        """Initialize empty processor registry."""
        self._processors: Dict[str, Type[MemoryProcessor]] = {}
        self._instances: Dict[str, MemoryProcessor] = {}
        self._default_processors: Dict[str, str] = {}

    def register_processor(
        self,
        name: str,
        processor_class: Type[MemoryProcessor],
        config: Optional[Dict[str, Any]] = None,
        is_default: bool = False,
        domain: Optional[str] = None
    ) -> None:
        """Register a processor class.

        Args:
            name: Unique processor name (e.g., "nb-whisper-large")
            processor_class: Processor implementation class
            config: Configuration for the processor
            is_default: Whether this is the default processor for its domain
            domain: Domain this processor belongs to (e.g., "speech")
        """
        logger.info(f"Registering processor: {name}")

        self._processors[name] = processor_class

        # Create instance
        try:
            instance = processor_class(config)
            self._instances[name] = instance
            logger.info(f"Successfully created instance for processor: {name}")
        except Exception as e:
            logger.error(f"Failed to create instance for processor {name}: {e}")
            raise

        # Set as default for domain if specified
        if is_default and domain:
            self._default_processors[domain] = name
            logger.info(f"Set {name} as default processor for domain: {domain}")

    async def process_with_processor(
        self,
        processor_name: str,
        content: bytes,
        metadata: Dict[str, Any]
    ) -> ProcessorResult:
        """Process content with a specific processor.

        Args:
            processor_name: Name of processor to use
            content: Input data to process
            metadata: Processing metadata and options

        Returns:
            ProcessorResult from the specified processor
        """
        if processor_name not in self._instances:
            available = list(self._instances.keys())
            raise ValueError(f"Processor '{processor_name}' not found. Available: {available}")

        processor = self._instances[processor_name]

        # Validate input
        if not processor.validate_input(content, metadata):
            raise ValueError(f"Input not valid for processor: {processor_name}")

        # Process
        try:
            logger.info(f"Processing with {processor_name}")
            result = await processor.process(content, metadata)
            logger.info(f"Processing completed with {processor_name}")
            return result
        except Exception as e:
            logger.error(f"Processing failed with {processor_name}: {e}")
            # Return error result instead of raising
            return ProcessorResult(
                processor=processor_name,
                status="failed",
                error=str(e)
            )

    async def process_with_multiple(
        self,
        processor_names: List[str],
        content: bytes,
        metadata: Dict[str, Any]
    ) -> List[ProcessorResult]:
        """Process content with multiple processors in parallel.

        Args:
            processor_names: List of processor names to use
            content: Input data to process
            metadata: Processing metadata and options

        Returns:
            List of ProcessorResults from all processors
        """
        tasks = []
        for processor_name in processor_names:
            task = self.process_with_processor(processor_name, content, metadata)
            tasks.append(task)

        # Run all processors in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to error results
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processor_name = processor_names[i]
                error_result = ProcessorResult(
                    processor=processor_name,
                    status="failed",
                    error=str(result)
                )
                final_results.append(error_result)
            else:
                final_results.append(result)

        return final_results

    def get_processor(self, name: str) -> Optional[MemoryProcessor]:
        """Get processor instance by name.

        Args:
            name: Processor name

        Returns:
            Processor instance or None if not found
        """
        return self._instances.get(name)

    def list_processors(self) -> List[str]:
        """Get list of all registered processor names.

        Returns:
            List of processor names
        """
        return list(self._instances.keys())

    def get_capabilities(self, processor_name: str) -> Optional[ProcessorCapabilities]:
        """Get capabilities for a specific processor.

        Args:
            processor_name: Name of processor

        Returns:
            ProcessorCapabilities or None if processor not found
        """
        processor = self.get_processor(processor_name)
        if processor:
            return processor.get_capabilities()
        return None

    def list_capabilities(self) -> Dict[str, ProcessorCapabilities]:
        """Get capabilities for all registered processors.

        Returns:
            Dictionary mapping processor names to their capabilities
        """
        capabilities = {}
        for name, processor in self._instances.items():
            capabilities[name] = processor.get_capabilities()
        return capabilities

    def get_default_processor(self, domain: str) -> Optional[str]:
        """Get default processor name for a domain.

        Args:
            domain: Domain name (e.g., "speech")

        Returns:
            Default processor name for the domain, or None
        """
        return self._default_processors.get(domain)

    async def health_check(self) -> Dict[str, bool]:
        """Check health of all processors.

        Returns:
            Dictionary mapping processor names to health status
        """
        health_status = {}
        for name, processor in self._instances.items():
            try:
                health_status[name] = await processor.health_check()
            except Exception as e:
                logger.error(f"Health check failed for {name}: {e}")
                health_status[name] = False

        return health_status


# Global registry instance
processor_registry = ProcessorRegistry()