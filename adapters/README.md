# Adapters

Adapters are the bridge between Meridian Core and a concrete agent runtime.

They may be prompts, `SKILL.md` files, system instructions, MCP wrappers, CLI
entrypoints, or future runtime integrations. They are not the core product.
Their job is to make an agent obey Meridian's lifecycle, artifact, state, and
evaluation protocols.

Current adapter families:

- `agent-skills/`: prompt-style skill packages for tools that can load
  instruction files.
