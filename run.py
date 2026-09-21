from pathlib import Path


def main() -> None:
    frontend_path = Path(__file__).parent / "app" / "frontend"
    print("Frontend workspace is ready.")
    print(f"Open the project in: {frontend_path}")
    print("Run `npm install` and `npm run dev` inside app/frontend to start the UI.")


if __name__ == "__main__":
    main()
