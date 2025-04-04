from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from typing import Type, TypeVar, List, Optional, Any

T = TypeVar("T")  # Generic model type


async def add_record(session: AsyncSession, model_class: Type[T], data: dict) -> T:
    """Add a new record to the database."""
    record = model_class(**data)
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record


async def get_by_id(session: AsyncSession, model_class: Type[T], record_id: int) -> Optional[T]:
    """Get a record by its ID."""
    return await session.get(model_class, record_id)


async def get_by_field(session: AsyncSession, model_class: Type[T], field: str, value: Any) -> Optional[T]:
    """Get a record by a specific field value, including JSON fields."""
    if '>>' in field:  # Handle JSON field queries
        stmt = select(model_class).where(text(f"{field} = :value"))
    else:
        stmt = select(model_class).where(getattr(model_class, field) == value)

    result = await session.execute(stmt, {'value': value})
    return result.scalar_one_or_none()


async def filter_by(
    session: AsyncSession,
    model_class: Type[T],
    order_by=None,
    limit=None,
    **filters
) -> List[T]:
    """Filter records by multiple criteria."""
    query = select(model_class)

    for key, value in filters.items():
        if '__' in key:  # Handle special filters like meta_data__type
            field, subfield = key.split('__', 1)
            query = query.where(text(f"{field}->'{subfield}' = :value_{key}"))
        else:
            query = query.where(getattr(model_class, key) == value)

    if order_by:
        query = query.order_by(*order_by)
    if limit:
        query = query.limit(limit)

    result = await session.execute(query, {f'value_{k}': v for k, v in filters.items()})
    return result.scalars().all()


async def update_record(session: AsyncSession, model_class: Type[T], record_id: int, updates: dict) -> Optional[T]:
    record = await session.get(model_class, record_id)
    if not record:
        return None
    for key, value in updates.items():
        setattr(record, key, value)
    await session.commit()
    await session.refresh(record)
    return record


async def delete_record(session: AsyncSession, model_class: Type[T], record_id: int) -> bool:
    """Delete a record by ID."""
    record = await session.get(model_class, record_id)
    if not record:
        return False
    await session.delete(record)
    await session.commit()
    return True
