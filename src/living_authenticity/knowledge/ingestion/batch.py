from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from src.living_authenticity.knowledge.ingestion.pipeline import (
    IngestionPipeline,
    IngestionResult,
)
from src.living_authenticity.security import PathBoundary


@dataclass
class IngestionOutcome:
    """Analysis-only outcome for one input file.

    Either ``result`` (success) or ``error`` (failure) is set, never both.
    The ``status`` string classifies the outcome.
    """

    source: str
    status: str
    result: IngestionResult | None = None
    error: str | None = None

    @property
    def is_success(self) -> bool:
        return self.result is not None


class BatchIngestor:
    """Orchestrates many single-file ingestions through the pipeline.

    Deterministic: inputs are processed in the order given.
    Error-isolating: a failure on one file is recorded in its own outcome
    and does not stop the remaining files.
    Default-deny: every input path is validated against a ``PathBoundary``
    before processing; a path outside the boundary is rejected with a clear
    error and is not read.
    Analysis-only: this layer never writes and never mutates anything.
    """

    def __init__(
        self,
        pipeline: IngestionPipeline,
        boundary: PathBoundary,
    ):
        self._pipeline = pipeline
        self._boundary = boundary

    def ingest_many(
        self,
        file_paths,
        *,
        on_failure: Callable[[IngestionOutcome], None] | None = None,
    ) -> list[IngestionOutcome]:
        """Ingest ``file_paths`` in order and return one outcome per input.

        ``on_failure`` is an optional hook called for each failed outcome.
        """

        outcomes: list[IngestionOutcome] = []

        for raw_path in file_paths:
            source = str(raw_path)

            if not self._boundary.is_allowed(source):
                outcome = IngestionOutcome(
                    source=source,
                    status="outside_boundary",
                    error="path is outside the allowed boundary",
                )
                self._report(outcome, on_failure)
                outcomes.append(outcome)
                continue

            path = Path(source)

            try:
                if not path.is_file():
                    if path.exists():
                        outcome = IngestionOutcome(
                            source=source,
                            status="invalid",
                            error="path is a directory, not a file",
                        )
                    else:
                        outcome = IngestionOutcome(
                            source=source,
                            status="invalid",
                            error="path is not a readable file",
                        )
                elif path.stat().st_size == 0:
                    outcome = IngestionOutcome(
                        source=source,
                        status="empty",
                        error="file is empty",
                    )
                else:
                    result = self._pipeline.ingest(source)
                    outcome = IngestionOutcome(
                        source=source,
                        status="success",
                        result=result,
                    )
                    outcomes.append(outcome)
                    continue
            except Exception as exc:
                outcome = IngestionOutcome(
                    source=source,
                    status="failed",
                    error=f"{type(exc).__name__}: {exc}",
                )

            self._report(outcome, on_failure)
            outcomes.append(outcome)

        return outcomes

    @staticmethod
    def _report(
        outcome: IngestionOutcome,
        on_failure: Callable[[IngestionOutcome], None] | None,
    ) -> None:
        if on_failure is not None:
            on_failure(outcome)