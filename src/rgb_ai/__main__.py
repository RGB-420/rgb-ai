from rgb_ai.config import load_config


def main() -> None:
    config = load_config()
    print(f"rgb-ai configured for Ollama at {config.ollama_base_url}")


if __name__ == "__main__":
    main()
