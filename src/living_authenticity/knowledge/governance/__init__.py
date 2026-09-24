"""Governance family (human authority, validation, side effects, trace).

Contains the only components allowed to touch authorization, validation,
controlled side effects, and traceability:

* ``approval``     -- explicit human authorization event
                       (single-proposal, hash-bound, non-transferable)
* ``revalidation`` -- fresh validity check of the exact approved proposal
                       immediately before execution
* ``execution``    -- the sole filesystem-writing component: one staged
                       ``CREATE`` artifact inside an explicit
                       ``PathBoundary``
* ``audit``        -- observational traceability record; authorizes and
                       executes nothing

Nothing in this family may be replaced by analytical output. Confidence,
similarity, and Knowledge Filter signals are not permission.

Deliberately contains no eager imports of the subpackages, so that
importing one governance member cannot trigger another family's chain.
"""
