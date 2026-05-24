import argparse

def setup_cli():
    parser = argparse.ArgumentParser(
        description="A grammar-based fuzzer for exposing client-server validation inconsistencies"
    )

    parser.add_argument(
        "-t", "--target", 
        required=True, 
        help="The target URL to fuzz (e.g., http://localhost:8080/registration)"
    )

    parser.add_argument(
        "-m", "--mode", 
        choices=['email', 'upload', 'params'], 
        required=True, 
        help="The type of input grammar to fuzz"
    )
    
    parser.add_argument(
        "-c", "--count",
        type=int,
        default=10,
        help="Number of fuzzing payloads to generate (default: 10)"
    )

    return parser.parse_args()