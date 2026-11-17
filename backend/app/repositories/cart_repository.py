import json
from redis.asyncio import Redis
from typing import Optional

from app.schemas.cart import Cart, CartItem
from app.db.redis import get_redis

class CartRepository:
    def __init__(self, redis_client: Optional[Redis] = None):
        self.redis = redis_client or get_redis()
        self.ttl_guest = 60 * 60 * 24 * 7  # 7 days
        self.ttl_user = 60 * 60 * 24 * 30  # 30 days

    def _get_key(self, cart_id: str) -> str:
        return f"cart:{cart_id}"

    async def get_cart(self, cart_id: str) -> Cart:
        key = self._get_key(cart_id)
        data = await self.redis.get(key)
        if data:
            return Cart.model_validate_json(data)
        return Cart(id=cart_id)

    async def save_cart(self, cart: Cart, is_guest: bool = True) -> None:
        key = self._get_key(cart.id)
        ttl = self.ttl_guest if is_guest else self.ttl_user
        
        # Calculate total price
        cart.total_price = sum(item.price_at_add * item.quantity for item in cart.items)
        
        await self.redis.set(key, cart.model_dump_json(), ex=ttl)

    async def add_item(self, cart_id: str, item: CartItem, is_guest: bool = True) -> Cart:
        cart = await self.get_cart(cart_id)
        
        # Check if item exists
        existing_item = next((i for i in cart.items if i.sku == item.sku), None)
        if existing_item:
            existing_item.quantity += item.quantity
        else:
            cart.items.append(item)
            
        await self.save_cart(cart, is_guest)
        return cart

    async def update_item_quantity(self, cart_id: str, sku: str, quantity: int, is_guest: bool = True) -> Cart:
        cart = await self.get_cart(cart_id)
        
        if quantity <= 0:
            return await self.remove_item(cart_id, sku, is_guest)
            
        for item in cart.items:
            if item.sku == sku:
                item.quantity = quantity
                break
                
        await self.save_cart(cart, is_guest)
        return cart

    async def remove_item(self, cart_id: str, sku: str, is_guest: bool = True) -> Cart:
        cart = await self.get_cart(cart_id)
        cart.items = [i for i in cart.items if i.sku != sku]
        await self.save_cart(cart, is_guest)
        return cart

    async def clear_cart(self, cart_id: str) -> None:
        key = self._get_key(cart_id)
        await self.redis.delete(key)

    async def merge_carts(self, guest_cart_id: str, user_cart_id: str) -> Cart:
        guest_cart = await self.get_cart(guest_cart_id)
        user_cart = await self.get_cart(user_cart_id)
        
        if not guest_cart.items:
            return user_cart

        # Simple merge: Add guest items to user cart
        for guest_item in guest_cart.items:
            existing_user_item = next((i for i in user_cart.items if i.sku == guest_item.sku), None)
            if existing_user_item:
                existing_user_item.quantity += guest_item.quantity
            else:
                user_cart.items.append(guest_item)
                
        await self.save_cart(user_cart, is_guest=False)
        await self.clear_cart(guest_cart_id)
        
        return user_cart
