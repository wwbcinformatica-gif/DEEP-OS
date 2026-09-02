"""
Rotas do Painel Administrativo
"""
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel

from core.auth import require_admin, AuthManager
from models.tenant import TenantCreate, TenantUpdate, TenantResponse
from models.plan import PlanType, DEFAULT_PLANS

router = APIRouter(prefix="/admin", tags=["Admin"])


# ─── Modelos de Request/Response ───────────────────────────────────

class DashboardStats(BaseModel):
    total_tenants: int
    active_tenants: int
    tenants_by_plan: dict
    mrr: float  # Monthly Recurring Revenue
    new_this_month: int


class TenantListItem(BaseModel):
    id: str
    name: str
    email: str
    plan: str
    status: str
    created_at: str
    last_login: Optional[str]


# ─── Dashboard ─────────────────────────────────────────────────────

@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(admin: str = Depends(require_admin)):
    """Retorna estatísticas do dashboard administrativo."""
    from database.connection import get_conn
    
    conn = get_conn()
    try:
        # Total de tenants
        total = conn.execute("SELECT COUNT(*) as count FROM tenants").fetchone()["count"]
        
        # Tenants ativos
        active = conn.execute(
            "SELECT COUNT(*) as count FROM tenants WHERE status = 'active'"
        ).fetchone()["count"]
        
        # Tenants por plano
        by_plan = {}
        for plan in PlanType:
            count = conn.execute(
                "SELECT COUNT(*) as count FROM tenants WHERE plan = ?",
                (plan.value,)
            ).fetchone()["count"]
            by_plan[plan.value] = count
        
        # MRR (Monthly Recurring Revenue)
        mrr = 0.0
        for plan_type, plan_data in DEFAULT_PLANS.items():
            count = by_plan.get(plan_type.value, 0)
            if plan_type == PlanType.ANNUAL:
                mrr += count * (plan_data["price"] / 12)
            elif plan_type == PlanType.QUARTERLY:
                mrr += count * (plan_data["price"] / 3)
            else:
                mrr += count * plan_data["price"]
        
        # Novos este mês
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0).isoformat()
        new_this_month = conn.execute(
            "SELECT COUNT(*) as count FROM tenants WHERE created_at >= ?",
            (month_start,)
        ).fetchone()["count"]
        
        return DashboardStats(
            total_tenants=total,
            active_tenants=active,
            tenants_by_plan=by_plan,
            mrr=round(mrr, 2),
            new_this_month=new_this_month
        )
    finally:
        conn.close()


# ─── Tenants CRUD ──────────────────────────────────────────────────

@router.get("/tenants")
async def list_tenants(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
    plan_filter: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    admin: str = Depends(require_admin)
):
    """Lista todos os tenants com paginação e filtros."""
    from database.connection import get_conn
    
    conn = get_conn()
    try:
        query = "SELECT * FROM tenants WHERE 1=1"
        params = []
        
        if status_filter:
            query += " AND status = ?"
            params.append(status_filter)
        
        if plan_filter:
            query += " AND plan = ?"
            params.append(plan_filter)
        
        if search:
            query += " AND (name LIKE ? OR email LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])
        
        # Count total
        count_query = query.replace("SELECT *", "SELECT COUNT(*) as count")
        total = conn.execute(count_query, params).fetchone()["count"]
        
        # Paginação
        offset = (page - 1) * limit
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        results = conn.execute(query, params).fetchall()
        
        tenants = [
            TenantListItem(
                id=r["id"],
                name=r["name"],
                email=r["email"],
                plan=r["plan"],
                status=r["status"],
                created_at=r["created_at"],
                last_login=r.get("last_login")
            )
            for r in results
        ]
        
        return {
            "tenants": tenants,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    finally:
        conn.close()


@router.get("/tenants/{tenant_id}")
async def get_tenant(
    tenant_id: str,
    admin: str = Depends(require_admin)
):
    """Retorna detalhes de um tenant específico."""
    from database.connection import get_conn
    
    conn = get_conn()
    try:
        result = conn.execute(
            "SELECT * FROM tenants WHERE id = ?",
            (tenant_id,)
        ).fetchone()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant não encontrado"
            )
        
        return dict(result)
    finally:
        conn.close()


@router.put("/tenants/{tenant_id}")
async def update_tenant(
    tenant_id: str,
    update: TenantUpdate,
    admin: str = Depends(require_admin)
):
    """Atualiza um tenant."""
    from database.connection import get_conn
    
    conn = get_conn()
    try:
        # Verifica se existe
        existing = conn.execute(
            "SELECT id FROM tenants WHERE id = ?",
            (tenant_id,)
        ).fetchone()
        
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant não encontrado"
            )
        
        # Monta update dinâmico
        updates = []
        params = []
        
        for field, value in update.model_dump(exclude_unset=True).items():
            if value is not None:
                updates.append(f"{field} = ?")
                params.append(value)
        
        if updates:
            updates.append("updated_at = ?")
            params.append(datetime.utcnow().isoformat())
            params.append(tenant_id)
            
            query = f"UPDATE tenants SET {', '.join(updates)} WHERE id = ?"
            conn.execute(query, params)
        
        return {"message": "Tenant atualizado com sucesso"}
    finally:
        conn.close()


@router.post("/tenants/{tenant_id}/suspend")
async def suspend_tenant(
    tenant_id: str,
    admin: str = Depends(require_admin)
):
    """Suspende um tenant."""
    from database.connection import get_conn
    
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE tenants SET status = 'suspended', updated_at = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), tenant_id)
        )
        return {"message": "Tenant suspenso com sucesso"}
    finally:
        conn.close()


@router.post("/tenants/{tenant_id}/reactivate")
async def reactivate_tenant(
    tenant_id: str,
    admin: str = Depends(require_admin)
):
    """Reativa um tenant."""
    from database.connection import get_conn
    
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE tenants SET status = 'active', updated_at = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), tenant_id)
        )
        return {"message": "Tenant reativado com sucesso"}
    finally:
        conn.close()


@router.delete("/tenants/{tenant_id}")
async def delete_tenant(
    tenant_id: str,
    admin: str = Depends(require_admin)
):
    """Deleta um tenant (soft delete)."""
    from database.connection import get_conn
    
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE tenants SET status = 'deleted', updated_at = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), tenant_id)
        )
        return {"message": "Tenant removido com sucesso"}
    finally:
        conn.close()


# ─── Planos ────────────────────────────────────────────────────────

@router.get("/plans")
async def list_plans(admin: str = Depends(require_admin)):
    """Lista todos os planos disponíveis."""
    return {
        "plans": [
            {
                "id": plan_data["id"].value,
                "name": plan_data["name"],
                "price": plan_data["price"],
                "interval": plan_data["interval"],
                "description": plan_data["description"],
                "features": plan_data["features"].model_dump(),
                "discount_percent": plan_data.get("discount_percent"),
                "includes_jarvis_lifetime": plan_data.get("includes_jarvis_lifetime", False),
            }
            for plan_data in DEFAULT_PLANS.values()
        ]
    }


# ─── Pagamentos ────────────────────────────────────────────────────

@router.get("/payments")
async def list_payments(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    tenant_id: Optional[str] = Query(None),
    admin: str = Depends(require_admin)
):
    """Lista pagamentos (placeholder - integração com gateway)."""
    return {
        "payments": [],
        "total": 0,
        "page": page,
        "limit": limit
    }
