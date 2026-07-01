from sqlalchemy.orm import joinedload
from database.models.Sale import Sale
from database.models.SaleDetail import SaleDetail
from services.base_service import BaseService


class SaleService(BaseService[Sale]):

    def get_paginated(self, db, skip: int, limit: int) -> list:
        return (
            db.query(Sale)
            .options(
                joinedload(Sale.client),
                joinedload(Sale.payment_method),
            )
            .order_by(Sale.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_with_details(self, db, sale_id) -> tuple:
        sale = (
            db.query(Sale)
            .options(
                joinedload(Sale.client),
                joinedload(Sale.payment_method),
            )
            .filter(Sale.id == sale_id)
            .first()
        )
        details = (
            db.query(SaleDetail)
            .options(joinedload(SaleDetail.product))
            .filter(SaleDetail.sale_id == sale_id)
            .all()
        )
        return sale, details


sale_service = SaleService(Sale)
