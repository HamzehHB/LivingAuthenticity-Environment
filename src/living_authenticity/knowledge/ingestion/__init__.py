"""Ingestion / preparation family.

Preparation only: read, clean, normalize, chunk, parse, extract units,
collect metadata. This family performs no analysis, no decision, no
authorization, and no filesystem write.

Deliberately contains no eager imports of the family's own modules.
``pipeline`` and ``batch`` depend on the analysis/decision families
(``IngestionPipeline`` keeps the optional classifier hook, and
``KnowledgeUnit`` now lives under ``ingestion.extraction``). Re-exporting
them from this ``__init__`` would create an import cycle
(ingestion -> analysis -> ingestion.extraction). The canonical import
paths are therefore the module paths:

    src.living_authenticity.knowledge.ingestion.pipeline
    src.living_authenticity.knowledge.ingestion.batch
"""
