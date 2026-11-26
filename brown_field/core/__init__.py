"""The core of the hexagon: the game, the accounts and the chat.

Nothing in this package does I/O. It reads the clock, draws random numbers,
hashes passwords and stores data only through the outbound ports in
`core.ports`. The adapters in `brown_field.adapters` implement those ports,
and `brown_field.game` wires them together (decision 0012).
"""
