from sqlalchemy import Column, Integer, String, Float, DateTime, func, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum


class OrderStatus(str, enum.Enum):
    PLACED = "PLACED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    total_price = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PLACED)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order(id={self.id}, total_price={self.total_price}, status={self.status})>"


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    food_item_id = Column(Integer, ForeignKey("food_items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)  # Price at time of order
    subtotal = Column(Float, nullable=False)  # quantity * unit_price

    # Relationships
    order = relationship("Order", back_populates="order_items")
    food_item = relationship("FoodItem", back_populates="order_items")

    def __repr__(self):
        return f"<OrderItem(order_id={self.order_id}, food_item_id={self.food_item_id}, qty={self.quantity})>"