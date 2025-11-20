"""
Base Block Class

Defines the interface that all blocks must implement for consistency and testability.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BlockStatus(Enum):
    """Block execution status"""
    NOT_CONFIGURED = "not_configured"
    CONFIGURED = "configured"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class BlockConfig:
    """Configuration for a block"""
    block_id: str
    block_type: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BlockOutput:
    """Output from a block execution"""
    block_id: str
    status: BlockStatus
    data: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class BaseBlock(ABC):
    """
    Base class for all recommender system blocks.

    Each block represents a modular, testable component in the recommendation pipeline.
    Blocks can be:
    - Input blocks (load data)
    - Transform blocks (process data)
    - Model blocks (train/apply algorithms)
    - Output blocks (generate results/metrics)
    """

    def __init__(self, block_id: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the block

        Args:
            block_id: Unique identifier for this block instance
            config: Configuration parameters for the block
        """
        self.block_id = block_id
        self.config = config or {}
        self.status = BlockStatus.NOT_CONFIGURED
        self.output: Optional[BlockOutput] = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    def configure(self, **kwargs) -> None:
        """
        Configure the block with parameters

        Args:
            **kwargs: Block-specific configuration parameters
        """
        pass

    @abstractmethod
    def validate_config(self) -> List[str]:
        """
        Validate the block configuration

        Returns:
            List of error messages (empty if valid)
        """
        pass

    @abstractmethod
    def execute(self, inputs: Dict[str, Any]) -> BlockOutput:
        """
        Execute the block's main functionality

        Args:
            inputs: Dictionary of input data from previous blocks

        Returns:
            BlockOutput containing results, metrics, and status
        """
        pass

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the input/output schema for this block

        Returns:
            Dictionary describing expected inputs and outputs
        """
        pass

    def reset(self) -> None:
        """Reset the block to initial state"""
        self.status = BlockStatus.NOT_CONFIGURED
        self.output = None
        self.logger.info(f"Block {self.block_id} reset")

    def get_output(self) -> Optional[BlockOutput]:
        """Get the output from the last execution"""
        return self.output

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id='{self.block_id}', status={self.status.value})"
