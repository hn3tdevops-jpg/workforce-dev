# Sample Packages

This directory contains example `.zip` package files for testing the package upload and validation feature.

## Creating a Sample Package

```bash
# Create a manifest
echo '{"name":"sample","version":"1.0.0","description":"A sample package"}' > manifest.json
zip sample_v1.0.0.zip manifest.json
```

## Manifest Fields

| Field | Required | Description |
|-------|----------|-------------|
| name | Yes | Package name |
| version | Yes | Semantic version |
| description | Yes | Short description |
