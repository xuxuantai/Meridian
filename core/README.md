# Meridian Core

`core/` contains the reusable analysis harness shared by all Meridian domain packs.

It defines:

- analysis contract templates
- analysis state templates
- consistency checks
- verification utilities

Domain packs should reuse these contracts instead of inventing separate state
mechanisms for every vertical use case.
