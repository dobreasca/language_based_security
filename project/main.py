from fuzzer.cli import setup_cli

def main():
    args = setup_cli()

    print("-" * 50)
    print("Grammar-based fuzzer initialized")
    print(f"[*] Target URL:  {args.target}")
    print(f"[*] Target Mode: {args.mode}")
    print(f"[*] Payload Vol: {args.count} tests")
    print("-" * 50)

    if args.mode == 'email':
        print("[*] Loading email grammar specifications...")
        # TODO: Hook up the exrex email mutation engine here
        
    elif args.mode == 'params':
        print("[*] Loading HTTP parameter specifications...")
        # TODO: Hook up parameter engine here

if __name__ == "__main__":
    main()