from schema import Optional, Schema

config = Schema(
    {
        Optional("host"): str,
        Optional("port"): int,
        Optional("password"): str,
    }
)
