"""Context Scene services (SG-155).

OpenRouter-routed scene rendering: one client module that restages an asset's
Evidence photo as a contextual scene image through OpenRouter's
OpenAI-compatible `/api/v1/chat/completions`. This is a library; T0 wires no
pipeline, opens no datastore and sends nothing (read-only, $0).
"""
