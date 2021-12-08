SELECT * 
FROM Product
INNER JOIN StoreProduct ON StoreProduct.product_id = Product.id
INNER JOIN ProductStatus ON ProductStatus.id = Product.product_status_id
WHERE StoreProduct.store_id = %s AND
ProductStatus.is_active = 1