"""
models.py - Data models with type safety and validation

This module provides dataclass-based models for all major data structures
in the application. Benefits:
- Type safety and autocomplete
- Automatic validation
- Better error messages
- Easier testing
- Clear data contracts
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class MappingItem:
    """
    Represents a single mapping between two items.

    Attributes:
        first_code: Code from First Group
        first_name: Name from First Group
        second_code: Code from Second Group (None if unmapped)
        second_name: Name from Second Group (None if unmapped)
        similarity_score: Similarity score (0-100)
        reasoning: Explanation for the similarity score
    """
    first_code: str
    first_name: str
    second_code: Optional[str]
    second_name: Optional[str]
    similarity_score: float
    reasoning: str

    def __post_init__(self):
        """Validate data after initialization"""
        if not 0 <= self.similarity_score <= 100:
            raise ValueError(
                f"Similarity score must be 0-100, got {self.similarity_score}"
            )

        if not self.first_code or not self.first_name:
            raise ValueError("First Group code and name are required")

        # Validate that mapped items have both code and name
        if self.second_code and not self.second_name:
            raise ValueError("Second Group name required when code is provided")
        if self.second_name and not self.second_code:
            raise ValueError("Second Group code required when name is provided")

    @property
    def is_mapped(self) -> bool:
        """Check if item has a valid mapping"""
        return (
            self.second_code is not None and
            self.second_name is not None and
            self.similarity_score > 0
        )

    @property
    def is_above_threshold(self) -> bool:
        """Check if similarity score is above threshold (imported at runtime)"""
        from core.config import Config
        return self.similarity_score >= Config.threshold

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary format for DataFrame compatibility.

        Returns:
            Dict: Dictionary with standard keys
        """
        return {
            "First Group Code": self.first_code,
            "First Group Name": self.first_name,
            "Second Group Code": self.second_code,
            "Second Group Name": self.second_name,
            "similarity score": self.similarity_score,
            "reason for similarity score": self.reasoning
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MappingItem':
        """
        Create MappingItem from dictionary.

        Args:
            data: Dictionary with mapping data

        Returns:
            MappingItem: New instance

        Raises:
            KeyError: If required keys are missing
        """
        return cls(
            first_code=data.get("First Group Code", ""),
            first_name=data.get("First Group Name", ""),
            second_code=data.get("Second Group Code"),
            second_name=data.get("Second Group Name"),
            similarity_score=data.get("similarity score", 0),
            reasoning=data.get("reason for similarity score", "")
        )


@dataclass
class BatchConfig:
    """
    Configuration for batch processing.

    Attributes:
        first_size: Number of items from First Group per batch
        second_size: Number of items from Second Group per batch
        total_batches: Total number of batches
        batches: List of batch dictionaries with ranges
    """
    first_size: int
    second_size: int
    total_batches: int
    batches: List[Dict[str, Any]]

    def __post_init__(self):
        """Validate batch configuration"""
        if self.total_batches < 1:
            raise ValueError("Must have at least 1 batch")

        if self.first_size < 1 or self.second_size < 1:
            raise ValueError("Batch sizes must be positive")

        if len(self.batches) != self.total_batches:
            raise ValueError(
                f"Batch list length ({len(self.batches)}) must match "
                f"total_batches ({self.total_batches})"
            )

    @property
    def max_items_per_batch(self) -> int:
        """Maximum total items per batch"""
        return self.first_size + self.second_size


@dataclass
class TokenUsage:
    """
    Token usage information from API call.

    Attributes:
        input_tokens: Tokens in the input (prompt + data)
        output_tokens: Tokens in the output (response)
        total_tokens: Total tokens used
    """
    input_tokens: int
    output_tokens: int
    total_tokens: int

    def __post_init__(self):
        """Validate token counts"""
        if self.input_tokens < 0 or self.output_tokens < 0:
            raise ValueError("Token counts must be non-negative")

        if self.total_tokens != self.input_tokens + self.output_tokens:
            raise ValueError(
                f"Total tokens ({self.total_tokens}) must equal "
                f"input ({self.input_tokens}) + output ({self.output_tokens})"
            )


@dataclass
class ProcessingResult:
    """
    Result of a mapping operation.

    Attributes:
        mappings: List of MappingItem objects
        token_usage: Token usage information
        elapsed_time: Time taken for processing (seconds)
        parameters_used: Configuration parameters used
        timestamp: When processing completed
        statistics: Optional statistics dictionary
    """
    mappings: List[MappingItem]
    token_usage: TokenUsage
    elapsed_time: float
    parameters_used: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    statistics: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate processing result"""
        if self.elapsed_time < 0:
            raise ValueError("Elapsed time must be non-negative")

        if not self.mappings:
            # Empty mappings list is allowed but log warning
            pass

    @property
    def mapped_count(self) -> int:
        """Count of successfully mapped items"""
        return sum(1 for m in self.mappings if m.is_mapped)

    @property
    def unmapped_count(self) -> int:
        """Count of unmapped items"""
        return len(self.mappings) - self.mapped_count

    @property
    def average_score(self) -> float:
        """Average similarity score for mapped items"""
        mapped = [m for m in self.mappings if m.is_mapped]
        if not mapped:
            return 0.0
        return sum(m.similarity_score for m in mapped) / len(mapped)

    @property
    def above_threshold_count(self) -> int:
        """Count of items above threshold"""
        return sum(1 for m in self.mappings if m.is_above_threshold)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary format.

        Returns:
            Dict: Dictionary representation
        """
        return {
            "mappings": [m.to_dict() for m in self.mappings],
            "token_usage": {
                "input": self.token_usage.input_tokens,
                "output": self.token_usage.output_tokens,
                "total": self.token_usage.total_tokens
            },
            "elapsed_time": self.elapsed_time,
            "parameters_used": self.parameters_used,
            "timestamp": self.timestamp.isoformat(),
            "statistics": self.statistics or {
                "mapped_count": self.mapped_count,
                "unmapped_count": self.unmapped_count,
                "average_score": self.average_score,
                "above_threshold": self.above_threshold_count
            }
        }


@dataclass
class APICallRecord:
    """
    Record of a single API call.

    Attributes:
        timestamp: When the call was made
        model: Model name used
        temperature: Temperature parameter
        top_p: Top P parameter
        max_batch_size: Maximum batch size
        wait_time: Wait time between batches
        latency: Time taken for API call (seconds)
        token_usage: Token usage information
        total_mappings: Total mappings in this call
        mapped_count: Number of successfully mapped items
        unmapped_count: Number of unmapped items
        avg_score: Average similarity score
    """
    timestamp: datetime
    model: str
    temperature: float
    top_p: float
    max_batch_size: int
    wait_time: int
    latency: float
    token_usage: TokenUsage
    total_mappings: int
    mapped_count: int
    unmapped_count: int
    avg_score: float

    def __post_init__(self):
        """Validate API call record"""
        if not 0 <= self.temperature <= 2:
            raise ValueError(f"Temperature must be 0-2, got {self.temperature}")

        if not 0 <= self.top_p <= 1:
            raise ValueError(f"Top P must be 0-1, got {self.top_p}")

        if self.latency < 0:
            raise ValueError("Latency must be non-negative")

        if not 0 <= self.avg_score <= 100:
            raise ValueError(f"Average score must be 0-100, got {self.avg_score}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DataFrame"""
        return {
            "Timestamp": self.timestamp,
            "Model": self.model,
            "Temperature": self.temperature,
            "Top P": self.top_p,
            "Max Batch Size": self.max_batch_size,
            "Wait Time": self.wait_time,
            "Latency": self.latency,
            "Input Tokens": self.token_usage.input_tokens,
            "Output Tokens": self.token_usage.output_tokens,
            "Total Tokens": self.token_usage.total_tokens,
            "Total Mappings": self.total_mappings,
            "Mapped Count": self.mapped_count,
            "Unmapped Count": self.unmapped_count,
            "Avg Score": self.avg_score
        }


# Type aliases for clarity
MappingList = List[MappingItem]
BatchList = List[Dict[str, Any]]
ParametersDict = Dict[str, Any]
