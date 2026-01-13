# 6Valley Product Agent

AI-powered product content generation system for e-commerce marketplaces. Generates bilingual (Russian + Uzbek) product descriptions, meta tags, and images using OpenAI.

## Features

- 🤖 **AI Product Text Generation**: Generates product names, descriptions, and meta tags in Russian and Uzbek
- 🖼️ **Image Generation**: Creates product images using DALL-E
- 🔌 **Venu API Integration**: Seamless integration with Venu marketplace API
- 🌐 **FastAPI REST API**: Modern, type-safe API with automatic documentation
- ⚙️ **Configuration Management**: Environment-based configuration
- 📝 **Comprehensive Logging**: Structured logging throughout the application

## Project Structure

```
6valley-product-agent/
├── agent/                    # AI agents
│   ├── product/              # Product text generation
│   │   ├── agent.py         # Main generation logic
│   │   └── schemas.py       # Pydantic schemas
│   └── image/               # Image generation
│       └── image_agent.py   # DALL-E integration
├── api/                      # External API integrations
│   └── venu_api.py         # Venu Seller API client
├── core/                     # Core utilities
│   ├── config.py           # Configuration management
│   └── openai_client.py    # OpenAI client singleton
├── utils/                    # Utility functions
│   └── logging_config.py   # Logging setup
├── api_models.py            # FastAPI request/response models
├── main.py                  # FastAPI application
└── requirements.txt         # Python dependencies
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd 6valley-product-agent
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file:
```bash
cp .env.example .env
```

5. Configure your `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key_here
VENU_EMAIL=your_venu_email@example.com
VENU_PASSWORD=your_venu_password
```

## Usage

### Running the API Server

```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Example API Request

```bash
curl -X POST "http://localhost:8000/generate-product" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "iPhone 15 Pro",
    "brand": "Apple",
    "price": 1500,
    "stock": 10
  }'
```

### Using the Venu API Client

```python
from api import VenuSellerAPI

api = VenuSellerAPI(email="your@email.com", password="password")
if api.login():
    result = api.add_product(
        name="Product Name",
        description="Product Description",
        # ... other parameters
    )
```

## Configuration

All configuration is managed through environment variables. See `.env.example` for available options.

### Key Settings

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: Model to use (default: `gpt-4o-mini`)
- `OPENAI_TEMPERATURE`: Generation temperature (default: `0.3`)
- `VENU_BASE_URL`: Venu API base URL (default: `https://api.venu.uz`)

## Development

### Code Quality

The project follows Python best practices:
- Type hints throughout
- Pydantic for data validation
- Comprehensive error handling
- Structured logging
- Modular architecture

### Adding New Features

1. Add new agents in `agent/` directory
2. Add API integrations in `api/` directory
3. Update schemas in respective `schemas.py` files
4. Add new endpoints in `main.py`

## License

[Your License Here]

## Contributing

[Contributing Guidelines Here]

