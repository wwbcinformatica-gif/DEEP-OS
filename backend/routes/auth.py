"""
Rotas de Autenticação para DEEP-OS SaaS
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr

from core.auth import AuthManager, get_current_tenant_id, AdminAuth
from models.tenant import (
    TenantCreate, TenantLogin, TenantResponse, TokenResponse,
    hash_password, verify_password
)
from models.plan import PlanType
from middleware.tenant import (
    get_tenant_db, create_tenant_dirs, TenantContext
)

router = APIRouter(prefix="/auth", tags=["Autenticação"])


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    company: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class AdminLoginRequest(BaseModel):
    email: str
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest):
    """Registra um novo tenant (assinante)."""
    conn = None
    try:
        # Conecta ao banco administrativo
        from database.connection import get_conn as get_admin_conn
        conn = get_admin_conn()
        
        # Verifica se o email já existe
        existing = conn.execute(
            "SELECT id FROM tenants WHERE email = ?",
            (req.email,)
        ).fetchone()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email já cadastrado"
            )
        
        # Gera ID único
        import secrets
        tenant_id = secrets.token_hex(16)
        
        # Hash da senha
        password_hash = AuthManager.hash_password(req.password)
        
        # Insere o tenant
        conn.execute("""
            INSERT INTO tenants (id, name, email, password_hash, plan, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            tenant_id,
            req.name,
            req.email,
            password_hash,
            PlanType.FREE.value,
            "active",
            datetime.utcnow().isoformat()
        ))
        
        # Cria diretórios do tenant
        create_tenant_dirs(tenant_id)
        
        # Gera token
        token = AuthManager.create_access_token({"sub": tenant_id})
        
        return TokenResponse(
            access_token=token,
            tenant=TenantResponse(
                id=tenant_id,
                name=req.name,
                email=req.email,
                plan=PlanType.FREE.value,
                status="active",
                license_key="",
                company=req.company,
                created_at=datetime.utcnow()
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao registrar: {str(e)}"
        )
    finally:
        if conn:
            conn.close()


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    """Autentica um tenant existente."""
    MASTER_EMAIL = "wwbc22@gmail.com"
    MASTER_PASSWORD = "admin123"

    # Master admin login
    if req.email == MASTER_EMAIL and req.password == MASTER_PASSWORD:
        token = AuthManager.create_access_token({
            "sub": "master-admin",
            "is_master": True
        })
        return TokenResponse(
            access_token=token,
            tenant=TenantResponse(
                id="master-admin",
                name="Master Admin",
                email=req.email,
                plan="master",
                status="active",
                license_key="",
                company="DEEP-OS",
                created_at=datetime.utcnow()
            )
        )

    conn = None
    try:
        from database.connection import get_conn as get_admin_conn
        conn = get_admin_conn()
        
        # Busca o tenant por email
        result = conn.execute(
            "SELECT * FROM tenants WHERE email = ?",
            (req.email,)
        ).fetchone()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha inválidos"
            )
        
        # Verifica a senha
        if not verify_password(req.password, result["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha inválidos"
            )
        
        # Verifica se está ativo
        if result["status"] != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Conta suspensa ou expirada"
            )
        
        # Atualiza último login
        conn.execute(
            "UPDATE tenants SET last_login = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), result["id"])
        )
        
        # Gera token
        token = AuthManager.create_access_token({"sub": result["id"]})
        
        return TokenResponse(
            access_token=token,
            tenant=TenantResponse(
                id=result["id"],
                name=result["name"],
                email=result["email"],
                plan=result["plan"],
                status=result["status"],
                license_key=result.get("license_key", ""),
                company=result.get("company"),
                created_at=datetime.fromisoformat(result["created_at"]),
                expires_at=datetime.fromisoformat(result["expires_at"]) if result.get("expires_at") else None
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao fazer login: {str(e)}"
        )
    finally:
        if conn:
            conn.close()


@router.post("/admin/login")
async def admin_login(req: AdminLoginRequest):
    """Login do painel administrativo com email e senha."""
    # Master admin credentials
    MASTER_EMAIL = "wwbc22@gmail.com"
    MASTER_PASSWORD = "admin123"
    
    if req.email != MASTER_EMAIL or req.password != MASTER_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha inválidos"
        )
    
    token = AdminAuth.create_admin_token()
    return {"access_token": token, "token_type": "bearer", "admin_email": req.email}


@router.get("/me", response_model=TenantResponse)
async def get_me(tenant_id: str = Depends(get_current_tenant_id)):
    """Retorna os dados do tenant autenticado."""
    conn = None
    try:
        from database.connection import get_conn as get_admin_conn
        conn = get_admin_conn()
        
        result = conn.execute(
            "SELECT * FROM tenants WHERE id = ?",
            (tenant_id,)
        ).fetchone()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant não encontrado"
            )
        
        return TenantResponse(
            id=result["id"],
            name=result["name"],
            email=result["email"],
            plan=result["plan"],
            status=result["status"],
            license_key=result.get("license_key", ""),
            company=result.get("company"),
            created_at=datetime.fromisoformat(result["created_at"]),
            expires_at=datetime.fromisoformat(result["expires_at"]) if result.get("expires_at") else None
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar dados: {str(e)}"
        )
    finally:
        if conn:
            conn.close()


@router.post("/change-password")
async def change_password(
    req: ChangePasswordRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Altera a senha do tenant."""
    conn = None
    try:
        from database.connection import get_conn as get_admin_conn
        conn = get_admin_conn()
        
        result = conn.execute(
            "SELECT password_hash FROM tenants WHERE id = ?",
            (tenant_id,)
        ).fetchone()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant não encontrado"
            )
        
        if not verify_password(req.current_password, result["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha atual incorreta"
            )
        
        new_hash = AuthManager.hash_password(req.new_password)
        conn.execute(
            "UPDATE tenants SET password_hash = ?, updated_at = ? WHERE id = ?",
            (new_hash, datetime.utcnow().isoformat(), tenant_id)
        )
        
        return {"message": "Senha alterada com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao alterar senha: {str(e)}"
        )
    finally:
        if conn:
            conn.close()


@router.post("/pix-key")
async def update_pix_key(
    pix_key: str,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Atualiza a chave PIX do tenant."""
    conn = None
    try:
        from database.connection import get_conn as get_admin_conn
        conn = get_admin_conn()
        
        conn.execute(
            "UPDATE tenants SET pix_key = ?, updated_at = ? WHERE id = ?",
            (pix_key, datetime.utcnow().isoformat(), tenant_id)
        )
        
        return {"message": "Chave PIX atualizada com sucesso", "pix_key": pix_key}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar chave PIX: {str(e)}"
        )
    finally:
        if conn:
            conn.close()


@router.post("/api-key")
async def update_api_key(
    api_key: str,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Atualiza a chave de API do tenant."""
    conn = None
    try:
        from database.connection import get_conn as get_admin_conn
        conn = get_admin_conn()
        
        conn.execute(
            "UPDATE tenants SET api_key = ?, updated_at = ? WHERE id = ?",
            (api_key, datetime.utcnow().isoformat(), tenant_id)
        )
        
        return {"message": "Chave de API atualizada com sucesso", "api_key": api_key}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar chave de API: {str(e)}"
        )
    finally:
        if conn:
            conn.close()
