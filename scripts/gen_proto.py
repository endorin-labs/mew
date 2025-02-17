from grpc_tools import protoc

protoc.main(
    (
        "",
        "-I.",
        "--python_out=.",
        "--grpclib_python_out=.",
        "--mypy_out=.",
        "app/proto/user/user.proto",
    )
)

protoc.main(
    (
        "",
        "-I.",
        "--python_out=.",
        "--grpclib_python_out=.",
        "--mypy_out=.",
        "app/proto/health/health.proto",
    )
)
