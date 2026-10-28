"""
Scheme Repository Layer.
Handles CRUD, filtering, pagination, and JSON seed loading for Government Scheme entities.
"""
import json
from typing import List, Optional, Tuple, Dict, Any
from pathlib import Path
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, or_
from backend.models.database import SchemeModel, CriterionRuleModel, SchemeSourceModel
from backend.schemas.scheme import SchemeFilterParams
from backend.core.logging import logger


class SchemeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, scheme_id: str) -> Optional[SchemeModel]:
        stmt = (
            select(SchemeModel)
            .options(joinedload(SchemeModel.rules), joinedload(SchemeModel.sources))
            .where(SchemeModel.scheme_id == scheme_id)
        )
        return self.db.scalars(stmt).unique().first()

    def get_all(
        self,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> List[SchemeModel]:
        stmt = (
            select(SchemeModel)
            .options(joinedload(SchemeModel.rules), joinedload(SchemeModel.sources))
        )
        if active_only:
            stmt = stmt.where(SchemeModel.is_active == True)
        stmt = stmt.offset(skip).limit(limit)
        return list(self.db.scalars(stmt).unique().all())

    def filter_schemes(
        self, params: SchemeFilterParams
    ) -> Tuple[List[SchemeModel], int]:
        stmt = select(SchemeModel).options(
            joinedload(SchemeModel.rules), joinedload(SchemeModel.sources)
        )

        conditions = []
        if params.status:
            conditions.append(SchemeModel.status == params.status)
        if params.category:
            conditions.append(SchemeModel.category.ilike(f"%{params.category}%"))
        if params.level:
            conditions.append(SchemeModel.level == params.level)
        if params.state:
            conditions.append(
                or_(SchemeModel.state == params.state, SchemeModel.state.is_(None))
            )
        if params.max_income is not None:
            conditions.append(
                or_(
                    SchemeModel.max_income.is_(None),
                    SchemeModel.max_income >= params.max_income,
                )
            )
        if params.age is not None:
            conditions.append(
                or_(SchemeModel.min_age.is_(None), SchemeModel.min_age <= params.age)
            )
            conditions.append(
                or_(SchemeModel.max_age.is_(None), SchemeModel.max_age >= params.age)
            )
        if params.search_query:
            q = f"%{params.search_query}%"
            conditions.append(
                or_(
                    SchemeModel.name.ilike(q),
                    SchemeModel.name_kannada.ilike(q),
                    SchemeModel.short_description.ilike(q),
                    SchemeModel.department.ilike(q),
                )
            )

        stmt = select(SchemeModel).options(
            joinedload(SchemeModel.rules), joinedload(SchemeModel.sources)
        )
        count_stmt = select(func.count(SchemeModel.id))

        for cond in conditions:
            stmt = stmt.where(cond)
            count_stmt = count_stmt.where(cond)

        total = self.db.scalar(count_stmt) or 0

        # Paginate
        skip = (params.page - 1) * params.page_size
        stmt = stmt.offset(skip).limit(params.page_size)
        results = list(self.db.scalars(stmt).unique().all())

        return results, total

    def upsert_scheme(self, data: Dict[str, Any]) -> SchemeModel:
        """Idempotently creates or updates a Scheme with nested rules and sources."""
        scheme_id = data["scheme_id"]
        scheme = self.get_by_id(scheme_id)

        rules_data = data.pop("rules", [])
        sources_data = data.pop("sources", [])

        if not scheme:
            scheme = SchemeModel(**{k: v for k, v in data.items() if hasattr(SchemeModel, k)})
            self.db.add(scheme)
            self.db.flush()
        else:
            for k, v in data.items():
                if hasattr(scheme, k):
                    setattr(scheme, k, v)
            # Remove old rules and sources to cleanly replace
            self.db.query(CriterionRuleModel).filter(CriterionRuleModel.scheme_id == scheme_id).delete()
            self.db.query(SchemeSourceModel).filter(SchemeSourceModel.scheme_id == scheme_id).delete()
            self.db.flush()

        # Add rules
        for r in rules_data:
            rule_obj = CriterionRuleModel(
                criterion_id=r.get("criterion_id", f"{scheme_id}_{r['field']}"),
                scheme_id=scheme_id,
                name=r.get("name", r["field"]),
                field=r["field"],
                operator=r.get("operator", "equals"),
                expected_value=r.get("expected_value"),
                is_mandatory=r.get("is_mandatory", True),
                source_citation=r.get("source_citation", "Official Portal"),
                description_kannada=r.get("description_kannada"),
                clarification_question_en=r.get("clarification_question_en"),
                clarification_question_kn=r.get("clarification_question_kn"),
            )
            self.db.add(rule_obj)

        # Add sources
        source_url = data.get("official_portal_url", "")
        if source_url:
            src_obj = SchemeSourceModel(
                scheme_id=scheme_id,
                source_url=source_url,
                source_title=data.get("source_title", "Official Portal"),
                last_checked_date=data.get("last_verified_date", "2025-01-01"),
                verification_status="verified",
                verification_notes=data.get("source_excerpt", ""),
            )
            self.db.add(src_obj)

        self.db.commit()
        return self.get_by_id(scheme_id)

    def seed_from_file(self, json_path: str) -> int:
        """Loads and upserts schemes from a JSON seed file."""
        path = Path(json_path)
        if not path.exists():
            logger.warning(f"Seed file not found: {json_path}")
            return 0

        with open(path, "r", encoding="utf-8") as f:
            items = json.load(f)

        count = 0
        for item in items:
            self.upsert_scheme(item)
            count += 1

        logger.info(f"Successfully seeded {count} schemes into database.")
        return count

    def count_schemes(self) -> int:
        """Returns total count of schemes in the database."""
        stmt = select(func.count(SchemeModel.id))
        return self.db.scalar(stmt) or 0

    def get_stats(self) -> Dict[str, Any]:
        """Returns statistics for administrative dashboard."""
        total = self.db.scalar(select(func.count(SchemeModel.id))) or 0
        active = self.db.scalar(select(func.count(SchemeModel.id)).where(SchemeModel.is_active == True)) or 0
        central = self.db.scalar(select(func.count(SchemeModel.id)).where(SchemeModel.level == "central")) or 0
        state = self.db.scalar(select(func.count(SchemeModel.id)).where(SchemeModel.level == "state")) or 0

        # Categories breakdown
        cat_rows = self.db.execute(
            select(SchemeModel.category, func.count(SchemeModel.id)).group_by(SchemeModel.category)
        ).all()
        categories = {row[0]: row[1] for row in cat_rows}

        return {
            "total_schemes": total,
            "active_schemes": active,
            "central_schemes": central,
            "state_schemes": state,
            "categories_breakdown": categories,
        }
