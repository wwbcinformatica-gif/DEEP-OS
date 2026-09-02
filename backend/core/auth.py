"""
Sistema de Autenticação JWT para DEEP-OS SaaS
"""
import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from passlib.context import CryptContext

# Configuração
SECRET_KEY = os.environ.get("JWT_SECRET", "DEEP-OS-saas-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 dias

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer(auto_error=False)


class AuthManager:
    """Gerencia autenticação e autorização."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Gera hash da senha."""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verifica se a senha corresponde ao hash."""
        return pwd_context.verify(password, hashed)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Cria um token JWT."""
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def decode_token(token: str) -> dict:
        """Decodifica e valida um token JWT."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )


def get_current_tenant_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    """Extrai o tenant_id do token JWT."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado"
        )
    
    payload = AuthManager.decode_token(credentials.credentials)
    tenant_id = payload.get("sub")
    
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    return tenant_id


def get_current_tenant_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """Versão opcional - retorna None se não autenticado."""
    if not credentials:
        return None
    
    try:
        payload = AuthManager.decode_token(credentials.credentials)
        return payload.get("sub")
    except Exception:
        return None


def require_plan(minimum_plan_level: int):
    """
    Dependency que verifica se o tenant tem o plano mínimo necessário.
    
    Uso:
        @router.get("/feature")
        async def feature(tenant_id: str = Depends(require_plan(1))):
            # 1 = monthly, 2 = quarterly, 3 = annual
            pass
    """
    from models.plan import PLAN_HIERARCHY
    
    def check_plan(
        tenant_id: str = Depends(get_current_tenant_id)
    ) -> str:
        from database.connection import get_conn
        
        conn = get_conn()
        try:
            result = conn.execute(
                "SELECT plan FROM tenants WHERE id = ?",
                (tenant_id,)
            ).fetchone()
            
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Tenant não encontrado"
                )
            
            tenant_plan = result["plan"]
            plan_level = PLAN_HIERARCHY.get(tenant_plan, 0)
            
            if plan_level < minimum_plan_level:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Plano insuficiente para esta funcionalidade"
                )
            
            return tenant_id
        finally:
            conn.close()
    
    return check_plan


def require_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Verifica se o usuário é administrador."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado"
        )
    
    payload = AuthManager.decode_token(credentials.credentials)
    
    if not payload.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    
    return payload.get("sub", "admin")


class AdminAuth:
    """Autenticação específica para o painel administrativo."""
    
    @staticmethod
    def create_admin_token(admin_id: str = "admin") -> str:
        """Cria token de administrador."""
        return AuthManager.create_access_token({
            "sub": admin_id,
            "is_admin": True
        })
    
    @staticmethod
    def verify_admin_password(password: str) -> bool:
        """Verifica senha do admin (configurada via variável de ambiente)."""
        admin_password = os.environ.get("ADMIN_PASSWORD", "DEEP-OS-admin")
        return password == admin_password
