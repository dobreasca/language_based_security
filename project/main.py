from __future__ import annotations

from fuzzer.cli import setup_cli
from fuzzer.payloads import generate_payloads
from fuzzer.report import print_summary, write_csv, write_json_summary
from fuzzer.sender import parse_headers, send_payloads


def main() -> None:
    args = setup_cli()

    print("-" * 60)
    print("Grammar-based fuzzer initialized")
    print(f"[*] Target URL:    {args.target}")
    print(f"[*] Target Mode:   {args.mode}")
    print(f"[*] Payload Vol:   {args.count} tests")
    print(f"[*] HTTP Method:   {args.method}")
    print(f"[*] Body Format:   {args.body_format}")
    print(f"[*] Field:         {args.field}")
    print(f"[*] Target Type:   {args.target_type}")
    print("-" * 60)

    payloads = generate_payloads(
        mode=args.mode,
        count=args.count,
        seed=args.seed,
        include_valid=not args.invalid_only,
    )

    if args.dry_run:
        for idx, payload in enumerate(payloads, start=1):
            print(
                f"#{idx:03d} expected_valid={payload.expected_valid} "
                f"strategy={payload.strategy} value={payload.value!r}"
            )
        return

    headers = parse_headers(args.header, args.bearer_token)

    results = send_payloads(
        payloads=payloads,
        target=args.target,
        method=args.method,
        body_format=args.body_format,
        field=args.field,
        target_type=args.target_type,
        upload_field=args.upload_field,
        headers=headers,
        timeout=args.timeout,
        verify_tls=not args.insecure,
        extra_fields=dict(
            field.split("=", 1) for field in args.extra_field
        ) if args.extra_field else {},
    )

    print_summary(results)
    write_csv(results, args.csv)
    write_json_summary(results, args.json_summary)

    print(f"\nWrote CSV results to: {args.csv}")
    print(f"Wrote JSON summary to: {args.json_summary}")


if __name__ == "__main__":
    main()