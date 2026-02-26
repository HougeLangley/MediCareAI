"""
Email Provider Presets API | 邮箱服务商预设API

提供预设的邮箱服务商配置列表
"""

import json
import os
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.deps import require_admin
from app.models.models import User

router = APIRouter()

# 预设配置文件路径
PROVIDERS_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "email_providers.json"
)


class SMTPConfig(BaseModel):
    """SMTP配置"""

    host: str
    port: int
    useTLS: bool
    useSSL: bool


class EmailProviderPreset(BaseModel):
    """邮箱服务商预设配置"""

    id: str
    name: str
    category: str
    categoryLabel: str
    icon: str
    description: str
    smtp: SMTPConfig
    helpText: str
    helpLink: Optional[str]


class ProviderCategory(BaseModel):
    """服务商分类"""

    label: str
    description: str
    icon: str


class EmailProvidersResponse(BaseModel):
    """邮箱服务商列表响应"""

    providers: List[EmailProviderPreset]
    categories: Dict[str, ProviderCategory]


def load_email_providers() -> Dict[str, Any]:
    """
    加载预设邮箱服务商配置

    Returns:
        Dict包含providers和categories
    """
    try:
        with open(PROVIDERS_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # 如果文件不存在，返回默认配置
        return {"providers": [], "categories": {}}
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"预设配置文件格式错误: {str(e)}",
        )


@router.get("/presets", response_model=EmailProvidersResponse)
async def get_email_provider_presets(
    current_user: User = Depends(require_admin),
) -> EmailProvidersResponse:
    """
    获取预设邮箱服务商列表 | Get email provider presets

    - 返回国内主流、国际服务和自定义选项
    - 包含SMTP配置、图标、帮助信息等
    """
    config = load_email_providers()

    # 构建分类信息
    categories = {}
    for cat_id, cat_info in config.get("categories", {}).items():
        categories[cat_id] = ProviderCategory(**cat_info)

    # 构建服务商列表
    providers = []
    for provider in config.get("providers", []):
        providers.append(EmailProviderPreset(**provider))

    return EmailProvidersResponse(providers=providers, categories=categories)


@router.get("/presets/{provider_id}", response_model=EmailProviderPreset)
async def get_email_provider_preset(
    provider_id: str,
    current_user: User = Depends(require_admin),
) -> EmailProviderPreset:
    """
    获取单个邮箱服务商预设 | Get single email provider preset

    Args:
        provider_id: 服务商ID (qq, gmail, custom等)
    """
    config = load_email_providers()

    for provider in config.get("providers", []):
        if provider["id"] == provider_id:
            return EmailProviderPreset(**provider)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"找不到ID为 {provider_id} 的邮箱服务商配置",
    )


@router.get("/presets-by-category/{category}", response_model=List[EmailProviderPreset])
async def get_email_providers_by_category(
    category: str,
    current_user: User = Depends(require_admin),
) -> List[EmailProviderPreset]:
    """
    按分类获取邮箱服务商 | Get email providers by category

    Args:
        category: 分类ID (domestic, international, custom)
    """
    config = load_email_providers()

    providers = []
    for provider in config.get("providers", []):
        if provider["category"] == category:
            providers.append(EmailProviderPreset(**provider))

    return providers
