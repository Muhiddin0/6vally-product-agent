# /generate-product Endpoint - Request Examples

## Endpoint
```
POST /generate-product
```

## Request Body Schema

```json
{
  "name": "string",      // Required: Product name (in Russian)
  "brand": "string",     // Required: Product brand
  "price": 0,            // Required: Product price (integer, >= 0)
  "stock": 5             // Optional: Stock quantity (default: 5, >= 0)
}
```

## Example 1: cURL

```bash
curl -X POST "http://localhost:8000/generate-product" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Смартфон Samsung Galaxy S24",
    "brand": "Samsung",
    "price": 899000,
    "stock": 10
  }'
```

## Example 2: Python (requests)

```python
import requests

url = "http://localhost:8000/generate-product"
payload = {
    "name": "Смартфон Samsung Galaxy S24",
    "brand": "Samsung",
    "price": 899000,
    "stock": 10
}

response = requests.post(url, json=payload)
print(response.json())
```

## Example 3: JavaScript (fetch)

```javascript
const response = await fetch('http://localhost:8000/generate-product', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    name: 'Смартфон Samsung Galaxy S24',
    brand: 'Samsung',
    price: 899000,
    stock: 10
  })
});

const data = await response.json();
console.log(data);
```

## Example 4: Minimal Request (stock optional)

```bash
curl -X POST "http://localhost:8000/generate-product" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ноутбук MacBook Pro",
    "brand": "Apple",
    "price": 2500000
  }'
```

## Example 5: Another Product

```bash
curl -X POST "http://localhost:8000/generate-product" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Наушники AirPods Pro",
    "brand": "Apple",
    "price": 350000,
    "stock": 25
  }'
```

## Response Example

```json
{
  "name": "Смартфон Samsung Galaxy S24",
  "description": "Современный флагманский смартфон с передовыми технологиями...",
  "meta_title": "Samsung Galaxy S24 - Купить в интернет-магазине",
  "meta_description": "Samsung Galaxy S24 с мощным процессором и отличной камерой...",
  "tags": ["смартфон", "samsung", "galaxy", "android", "флагман"],
  "price": 899000,
  "stock": 10,
  "shop_saved": true,
  "shop_response": {
    "product_id": "12345",
    "status": "success"
  }
}
```

## Notes

- `name` va `brand` majburiy maydonlar (minimal uzunlik: 1)
- `price` majburiy, manfiy bo'lishi mumkin emas (>= 0)
- `stock` ixtiyoriy, default qiymati: 5
- `name` rus tilida bo'lishi kerak
- API avtomatik ravishda mahsulot tasvirlarini yaratadi va do'konga saqlaydi
