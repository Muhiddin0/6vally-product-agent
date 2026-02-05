
Remove image

Method: GET
URL
https://api.venu.uz/api/v3/seller/products/delete-image?id=13604&name=2026-02-03-6981a4111337e.webp&color=null
Headers
accept-encoding:
gzip
authorization:
Bearer VNFbhU6Fr17tNTmrDMvdSVOJonk8wOp9KT4Su7Wm3jkUS1DuG8
content-type:
application/json; charset=UTF-8
host:
api.venu.uz
user-agent:
Dart/3.10 (dart:io)

Response
Status: 200 OK
Headers
Access-Control-Allow-Headers:
*
Access-Control-Allow-Methods:
*
Access-Control-Allow-Origin:
*
Cache-Control:
no-cache, private
Connection:
keep-alive
Content-Length:
36
Content-Type:
application/json
Date:
Tue, 03 Feb 2026 10:02:11 GMT
Server:
openresty
X-Powered-By:
PHP/8.3.29
X-Ratelimit-Limit:
3000
X-Ratelimit-Remaining:
3000
X-Served-By:
api.venu.uz


Response body
"Product image removed successfully"


Get product images

Request
Method: GET
URL
https://api.venu.uz/api/v3/seller/products/get-product-images/13604
Headers
accept-encoding:
gzip
authorization:
Bearer VNFbhU6Fr17tNTmrDMvdSVOJonk8wOp9KT4Su7Wm3jkUS1DuG8
content-type:
application/json; charset=UTF-8
host:
api.venu.uz
user-agent:
Dart/3.10 (dart:io)

Response
Status: 200 OK
Headers
Access-Control-Allow-Headers:
*
Access-Control-Allow-Methods:
*
Access-Control-Allow-Origin:
*
Cache-Control:
no-cache, private
Connection:
keep-alive
Content-Length:
406
Content-Type:
application/json
Date:
Tue, 03 Feb 2026 10:02:29 GMT
Server:
openresty
X-Powered-By:
PHP/8.3.29
X-Ratelimit-Limit:
3000
X-Ratelimit-Remaining:
2999
X-Served-By:
api.venu.uz

Response body
{
"images": [
{
"image_name": "2026-02-03-6981a40de117b.webp",
"storage": "public"
},
{
"image_name": "2026-02-03-6981a4156170d.webp",
"storage": "public"
}
],
"color_image": [],
"images_full_url": [
{
"key": "2026-02-03-6981a40de117b.webp",
"path": null,
"status": 404
},
{
"key": "2026-02-03-6981a4156170d.webp",
"path": "https:\/\/api.venu.uz\/storage\/product\/2026-02-03-6981a4156170d.webp",
"status": 200
}
],
"color_images_full_url": []
}




Update status

Request
Method: POST
URL
https://api.venu.uz/api/v3/seller/products/status-update
Headers
accept-encoding:
gzip
authorization:
Bearer VNFbhU6Fr17tNTmrDMvdSVOJonk8wOp9KT4Su7Wm3jkUS1DuG8
content-length:
39
content-type:
application/json; charset=UTF-8
host:
api.venu.uz
user-agent:
Dart/3.10 (dart:io)

Response
Status: 200 OK
Headers
Access-Control-Allow-Headers:
*
Access-Control-Allow-Methods:
*
Access-Control-Allow-Origin:
*
Cache-Control:
no-cache, private
Connection:
keep-alive
Content-Length:
40
Content-Type:
application/json
Date:
Tue, 03 Feb 2026 10:07:25 GMT
Server:
openresty
X-Powered-By:
PHP/8.3.29
X-Ratelimit-Limit:
3000
X-Ratelimit-Remaining:
3000
X-Served-By:
api.venu.uz

Request body
{
"id": 13604,
"status": 1,
"_method": "put"
}


Response body
{
"success": "Status update successfully"
}



Detail api
Method: GET
URL
https://api.venu.uz/api/v3/seller/products/details/13604
Headers
accept-encoding:
gzip
authorization:
Bearer VNFbhU6Fr17tNTmrDMvdSVOJonk8wOp9KT4Su7Wm3jkUS1DuG8
content-type:
application/json; charset=UTF-8
host:
api.venu.uz
user-agent:
Dart/3.10 (dart:io)

Response
Status: 200 OK
Headers
Access-Control-Allow-Headers:
*
Access-Control-Allow-Methods:
*
Access-Control-Allow-Origin:
*
Cache-Control:
no-cache, private
Connection:
keep-alive
Content-Type:
application/json
Date:
Tue, 03 Feb 2026 10:17:55 GMT
Server:
openresty
Transfer-Encoding:
chunked
X-Powered-By:
PHP/8.3.29
X-Ratelimit-Limit:
3000
X-Ratelimit-Remaining:
2997
X-Served-By:
api.venu.uz

Response body
{
"id": 13604,
"added_by": "seller",
"user_id": 35,
"name": "Lattafa Her Confession 100\u043c\u043b",
"slug": "lattafa-her-confession-100ml-MSIgY3",
"product_type": "physical",
"category_ids": [
{
"id": "429",
"position": 1
},
{
"id": "600",
"position": 2
},
{
"id": "601",
"position": 3
}
],
"category_id": 429,
"sub_category_id": 600,
"sub_sub_category_id": 601,
"brand_id": 1,
"unit": "pc",
"min_qty": 1,
"refundable": 1,
"digital_product_type": null,
"digital_file_ready": null,
"digital_file_ready_storage_type": "public",
"images": "[{\"image_name\":\"2026-02-03-6981a40de117b.webp\",\"storage\":\"public\"},{\"image_name\":\"2026-02-03-6981a4156170d.webp\",\"storage\":\"public\"}]",
"color_image": "[]",
"thumbnail": "2026-02-03-6981a40de117b.webp",
"thumbnail_storage_type": "public",
"preview_file": "",
"preview_file_storage_type": null,
"featured": null,
"flash_deal": null,
"video_provider": "youtube",
"video_url": null,
"colors": [],
"variant_product": 0,
"attributes": [],
"choice_options": [],
"variation": [],
"digital_product_file_types": [],
"digital_product_extensions": [],
"published": 0,
"unit_price": 80,
"purchase_price": 0,
"tax": 0,
"tax_type": "percent",
"tax_model": "exclude",
"discount": 0,
"discount_type": "flat",
"current_stock": 15,
"minimum_order_qty": 1,
"details": "<p>Lattafa Her Confession \u2014 \u044d\u0442\u043e \u0430\u0440\u043e\u043c\u0430\u0442, \u043a\u043e\u0442\u043e\u0440\u044b\u0439 \u0440\u0430\u0441\u0441\u043a\u0430\u0436\u0435\u0442 \u0432\u0430\u0448\u0443 \u0438\u0441\u0442\u043e\u0440\u0438\u044e. \ud83c\udf39 \u041f\u043e\u0433\u0440\u0443\u0437\u0438\u0442\u0435\u0441\u044c \u0432 \u043c\u0438\u0440 \u0443\u0442\u043e\u043d\u0447\u0435\u043d\u043d\u043e\u0441\u0442\u0438 \u0438 \u044d\u043b\u0435\u0433\u0430\u043d\u0442\u043d\u043e\u0441\u0442\u0438 \u0441 \u043a\u0430\u0436\u0434\u043e\u0439 \u043a\u0430\u043f\u043b\u0435\u0439 \u044d\u0442\u043e\u0433\u043e \u043f\u0430\u0440\u0444\u044e\u043c\u0430.<\/p><p>\u0421\u043e\u0437\u0434\u0430\u043d\u043d\u044b\u0439 \u0434\u043b\u044f \u0443\u0432\u0435\u0440\u0435\u043d\u043d\u044b\u0445 \u0432 \u0441\u0435\u0431\u0435 \u0436\u0435\u043d\u0449\u0438\u043d, \u044d\u0442\u043e\u0442 \u0430\u0440\u043e\u043c\u0430\u0442 \u0441\u043e\u0447\u0435\u0442\u0430\u0435\u0442 \u0432 \u0441\u0435\u0431\u0435 \u0441\u043b\u0430\u0434\u043a\u0438\u0435 \u0438 \u0446\u0432\u0435\u0442\u043e\u0447\u043d\u044b\u0435 \u043d\u043e\u0442\u044b, \u043a\u043e\u0442\u043e\u0440\u044b\u0435 \u043e\u0441\u0442\u0430\u0432\u043b\u044f\u044e\u0442 \u043d\u0435\u0437\u0430\u0431\u044b\u0432\u0430\u0435\u043c\u043e\u0435 \u0432\u043f\u0435\u0447\u0430\u0442\u043b\u0435\u043d\u0438\u0435. \u2728<\/p><ul><li>\ud83d\udc8e \u0423\u043d\u0438\u043a\u0430\u043b\u044c\u043d\u0430\u044f \u043a\u043e\u043c\u043f\u043e\u0437\u0438\u0446\u0438\u044f \u2014 \u0441\u043e\u0447\u0435\u0442\u0430\u043d\u0438\u0435 \u0444\u0440\u0443\u043a\u0442\u043e\u0432\u044b\u0445 \u0438 \u0446\u0432\u0435\u0442\u043e\u0447\u043d\u044b\u0445 \u0430\u043a\u0446\u0435\u043d\u0442\u043e\u0432.<\/li><li>\u26a1 \u0414\u043e\u043b\u0433\u043e\u0432\u0435\u0447\u043d\u043e\u0441\u0442\u044c \u2014 \u0430\u0440\u043e\u043c\u0430\u0442 \u0431\u0443\u0434\u0435\u0442 \u0441\u043e\u043f\u0440\u043e\u0432\u043e\u0436\u0434\u0430\u0442\u044c \u0432\u0430\u0441 \u043d\u0430 \u043f\u0440\u043e\u0442\u044f\u0436\u0435\u043d\u0438\u0438 \u0432\u0441\u0435\u0433\u043e \u0434\u043d\u044f.<\/li><li>\ud83c\udfaf \u0418\u0434\u0435\u0430\u043b\u0435\u043d \u0434\u043b\u044f \u043b\u044e\u0431\u043e\u0433\u043e \u0441\u043b\u0443\u0447\u0430\u044f \u2014 \u043e\u0442 \u0440\u043e\u043c\u0430\u043d\u0442\u0438\u0447\u0435\u0441\u043a\u043e\u0433\u043e \u0432\u0435\u0447\u0435\u0440\u0430 \u0434\u043e \u0434\u0435\u043b\u043e\u0432\u043e\u0439 \u0432\u0441\u0442\u0440\u0435\u0447\u0438.<\/li><li>\ud83d\udd10 \u042d\u043b\u0435\u0433\u0430\u043d\u0442\u043d\u044b\u0439 \u0444\u043b\u0430\u043a\u043e\u043d \u2014 \u0441\u0442\u0430\u043d\u0435\u0442 \u043d\u0430\u0441\u0442\u043e\u044f\u0449\u0438\u043c \u0443\u043a\u0440\u0430\u0448\u0435\u043d\u0438\u0435\u043c \u0432\u0430\u0448\u0435\u0433\u043e \u0442\u0443\u0430\u043b\u0435\u0442\u043d\u043e\u0433\u043e \u0441\u0442\u043e\u043b\u0438\u043a\u0430.<\/li><li>\ud83d\ude80 \u041b\u0435\u0433\u043a\u043e\u0441\u0442\u044c \u0438 \u0441\u0432\u0435\u0436\u0435\u0441\u0442\u044c \u2014 \u0438\u0434\u0435\u0430\u043b\u044c\u043d\u044b\u0439 \u0432\u044b\u0431\u043e\u0440 \u0434\u043b\u044f \u0442\u0435\u043f\u043b\u044b\u0445 \u0434\u043d\u0435\u0439.<\/li><\/ul><p>\u041d\u0435 \u0443\u043f\u0443\u0441\u0442\u0438\u0442\u0435 \u0448\u0430\u043d\u0441 \u0434\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u044d\u0442\u043e\u0442 \u0448\u0435\u0434\u0435\u0432\u0440 \u0432 \u0441\u0432\u043e\u044e \u043a\u043e\u043b\u043b\u0435\u043a\u0446\u0438\u044e \u2014 Lattafa Her Confession \u0436\u0434\u0435\u0442 \u0432\u0430\u0441!<\/p>",
"free_shipping": 0,
"attachment": null,
"created_at": "2026-02-03T07:30:30.000000Z",
"updated_at": "2026-02-03T10:07:25.000000Z",
"status": 1,
"featured_status": 1,
"meta_title": null,
"meta_description": null,
"meta_image": null,
"request_status": 1,
"denied_note": null,
"shipping_cost": 0,
"multiply_qty": 0,
"temp_shipping_cost": null,
"is_shipping_cost_updated": null,
"code": "0B4304",
"mxik": "0",
"weight": "300",
"height": "150",
"width": "50",
"length": "50",
"package_code": "0",
"is_install": 0,
"is_seasonal": 0,
"is_discount": 0,
"reviews_count": 0,
"colors_formatted": [],
"is_shop_temporary_close": 0,
"thumbnail_full_url": {
"key": "2026-02-03-6981a40de117b.webp",
"path": "https:\/\/api.venu.uz\/storage\/product\/thumbnail\/2026-02-03-6981a40de117b.webp",
"status": 200
},
"preview_file_full_url": {
"key": "",
"path": null,
"status": 404
},
"color_images_full_url": [],
"meta_image_full_url": {
"key": null,
"path": null,
"status": 404
},
"images_full_url": [
{
"key": "2026-02-03-6981a40de117b.webp",
"path": null,
"status": 404
},
{
"key": "2026-02-03-6981a4156170d.webp",
"path": "https:\/\/api.venu.uz\/storage\/product\/2026-02-03-6981a4156170d.webp",
"status": 200
}
],
"digital_file_ready_full_url": {
"key": null,
"path": null,
"status": 404
},
"seo_info": {
"id": 8429,
"product_id": 13604,
"title": "Lattafa Her Confession 100\u043c\u043b - \u0410\u0440\u043e\u043c\u0430\u0442 \u0434\u043b\u044f \u0436\u0435\u043d\u0449\u0438\u043d",
"description": "\u041e\u0442\u043a\u0440\u043e\u0439\u0442\u0435 \u0434\u043b\u044f \u0441\u0435\u0431\u044f Lattafa Her Confession 100\u043c\u043b \u2014 \u0430\u0440\u043e\u043c\u0430\u0442, \u043a\u043e\u0442\u043e\u0440\u044b\u0439 \u043f\u043e\u0434\u0447\u0435\u0440\u043a\u043d\u0435\u0442 \u0432\u0430\u0448\u0443 \u0438\u043d\u0434\u0438\u0432\u0438\u0434\u0443\u0430\u043b\u044c\u043d\u043e\u0441\u0442\u044c \u0438 \u044d\u043b\u0435\u0433\u0430\u043d\u0442\u043d\u043e\u0441\u0442\u044c.",
"index": "noindex",
"no_follow": "",
"no_image_index": "",
"no_archive": "",
"no_snippet": "0",
"max_snippet": "0",
"max_snippet_value": "0",
"max_video_preview": "0",
"max_video_preview_value": "0",
"max_image_preview": "0",
"max_image_preview_value": "large",
"image": "\/tmp\/excel_images_2ll4un8v\/row5_main.png",
"created_at": "2026-02-03T07:30:30.000000Z",
"updated_at": "2026-02-03T07:30:30.000000Z",
"image_full_url": {
"key": "\/tmp\/excel_images_2ll4un8v\/row5_main.png",
"path": null,
"status": 404
},
"storage": [
{
"id": 8501,
"data_type": "App\\Models\\ProductSeo",
"data_id": "8429",
"key": "image",
"value": "public",
"created_at": "2026-02-03T07:30:30.000000Z",
"updated_at": "2026-02-03T07:30:30.000000Z"
}
]
},
"digital_product_authors": [],
"digital_product_publishing_house": [],
"clearance_sale": null,
"translations": [],
"reviews": []
}