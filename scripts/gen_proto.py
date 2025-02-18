import glob
from grpc_tools import protoc


def generate_proto_files():
    proto_files = glob.glob("app/proto/**/*.proto", recursive=True)

    for proto_file in proto_files:
        print(f"Generating stubs for {proto_file}")
        protoc.main(
            (
                "",
                "-I.",  # include path
                "--python_out=.",
                "--grpclib_python_out=.",
                "--mypy_out=.",
                proto_file,
            )
        )


if __name__ == "__main__":
    generate_proto_files()
