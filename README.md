# envdiff

> Compare `.env` files across environments and highlight missing or mismatched keys.

---

## Installation

```bash
pip install envdiff
```

Or install from source:

```bash
git clone https://github.com/yourname/envdiff.git
cd envdiff
pip install .
```

---

## Usage

```bash
envdiff .env.development .env.production
```

**Example output:**

```
Missing in .env.production:
  - DATABASE_URL
  - DEBUG

Mismatched values:
  - API_BASE_URL
      development: http://localhost:8000
      production:  https://api.example.com

✔ All other keys match.
```

You can also compare more than two files at once:

```bash
envdiff .env.development .env.staging .env.production
```

Use the `--keys-only` flag to suppress value output and show only key differences:

```bash
envdiff .env.development .env.production --keys-only
```

---

## Why envdiff?

Keeping multiple environment files in sync is error-prone. `envdiff` gives you a fast, readable diff focused specifically on `.env` structure — not line-by-line text changes.

---

## License

This project is licensed under the [MIT License](LICENSE).