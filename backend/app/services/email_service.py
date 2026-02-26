"""
Email Service | 邮件服务

提供邮件发送功能，包括：
- 邮箱验证邮件
- 密码重置邮件
- 系统通知邮件

使用异步任务队列发送邮件，避免阻塞主线程
"""

import smtplib
import uuid
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.models.models import User
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """邮件服务类 | Email Service Class"""

    def __init__(self):
        self.smtp_host = getattr(settings, "smtp_host", None)
        self.smtp_port = getattr(settings, "smtp_port", 587)
        self.smtp_user = getattr(settings, "smtp_user", None)
        self.smtp_password = getattr(settings, "smtp_password", None)
        self.from_email = getattr(settings, "smtp_from_email", None)
        self.from_name = getattr(settings, "smtp_from_name", "MediCareAI")
        self.use_tls = getattr(settings, "smtp_use_tls", True)

        # 检查邮件服务是否可用
        self.is_available = all(
            [self.smtp_host, self.smtp_user, self.smtp_password, self.from_email]
        )

        if not self.is_available:
            logger.warning(
                "Email service not configured. Email functionality will be disabled."
            )

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """
        发送邮件 | Send Email

        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            html_content: HTML内容
            text_content: 纯文本内容（可选）

        Returns:
            bool: 发送是否成功
        """
        if not self.is_available:
            logger.warning(
                f"Email service not available. Would have sent email to {to_email}"
            )
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = formataddr((self.from_name, self.from_email))
            msg["To"] = to_email

            # 添加纯文本版本
            if text_content:
                msg.attach(MIMEText(text_content, "plain", "utf-8"))

            # 添加HTML版本
            msg.attach(MIMEText(html_content, "html", "utf-8"))

            # 连接SMTP服务器并发送
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, to_email, msg.as_string())

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    async def send_verification_email(
        self, db: AsyncSession, user: User, base_url: str
    ) -> Optional[str]:
        """
        发送邮箱验证邮件 | Send Verification Email

        Args:
            db: 数据库会话
            user: 用户对象
            base_url: 基础URL（用于构建验证链接）

        Returns:
            str: 验证token，失败返回None
        """
        # 生成验证token
        verification_token = str(uuid.uuid4())

        # 保存token到用户记录
        user.email_verification_token = verification_token
        user.email_verification_sent_at = datetime.utcnow()
        await db.commit()

        # 构建验证链接
        verification_url = f"{base_url}/verify-email?token={verification_token}"

        # 邮件内容
        subject = "【MediCareAI】邮箱验证 - Email Verification"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>MediCareAI 邮箱验证</h1>
                    <h2>Email Verification</h2>
                </div>
                <div class="content">
                    <p>尊敬的 {user.full_name}，您好！</p>
                    <p>感谢您注册 MediCareAI 智能疾病管理系统。为了确保您的账户安全，请验证您的邮箱地址。</p>
                    <p>Dear {user.full_name}, thank you for registering with MediCareAI. Please verify your email address to secure your account.</p>
                    
                    <div style="text-align: center;">
                        <a href="{verification_url}" class="button">点击验证邮箱 / Verify Email</a>
                    </div>
                    
                    <p>或者复制以下链接到浏览器打开：</p>
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="background: #eee; padding: 10px; border-radius: 5px; word-break: break-all;">{verification_url}</p>
                    
                    <p>此链接将在24小时后失效。如非本人操作，请忽略此邮件。</p>
                    <p>This link will expire in 24 hours. If you didn't request this, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>MediCareAI 智能疾病管理系统</p>
                    <p>本邮件由系统自动发送，请勿回复</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        MediCareAI 邮箱验证
        
        尊敬的 {user.full_name}，您好！
        
        感谢您注册 MediCareAI 智能疾病管理系统。请验证您的邮箱地址：
        
        {verification_url}
        
        此链接将在24小时后失效。如非本人操作，请忽略此邮件。
        
        MediCareAI 智能疾病管理系统
        """

        success = await self.send_email(user.email, subject, html_content, text_content)

        if success:
            return verification_token
        else:
            return None

    async def send_password_reset_email(
        self, db: AsyncSession, user: User, base_url: str
    ) -> Optional[str]:
        """
        发送密码重置邮件 | Send Password Reset Email

        Args:
            db: 数据库会话
            user: 用户对象
            base_url: 基础URL（用于构建重置链接）

        Returns:
            str: 重置token，失败返回None
        """
        # 生成重置token
        reset_token = str(uuid.uuid4())

        # 保存token到用户记录
        user.password_reset_token = reset_token
        user.password_reset_sent_at = datetime.utcnow()
        await db.commit()

        # 构建重置链接
        reset_url = f"{base_url}/reset-password?token={reset_token}"

        # 邮件内容
        subject = "【MediCareAI】密码重置 - Password Reset"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
                .warning {{ color: #f44336; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>MediCareAI 密码重置</h1>
                    <h2>Password Reset</h2>
                </div>
                <div class="content">
                    <p>尊敬的 {user.full_name}，您好！</p>
                    <p>我们收到了您的密码重置请求。如果这不是您本人的操作，请忽略此邮件。</p>
                    <p>Dear {user.full_name}, we received a password reset request for your account. If you didn't request this, please ignore this email.</p>
                    
                    <div style="text-align: center;">
                        <a href="{reset_url}" class="button">重置密码 / Reset Password</a>
                    </div>
                    
                    <p>或者复制以下链接到浏览器打开：</p>
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="background: #eee; padding: 10px; border-radius: 5px; word-break: break-all;">{reset_url}</p>
                    
                    <p class="warning">此链接将在1小时后失效，请尽快操作。</p>
                    <p class="warning">This link will expire in 1 hour.</p>
                </div>
                <div class="footer">
                    <p>MediCareAI 智能疾病管理系统</p>
                    <p>本邮件由系统自动发送，请勿回复</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        MediCareAI 密码重置
        
        尊敬的 {user.full_name}，您好！
        
        我们收到了您的密码重置请求。请点击以下链接重置密码：
        
        {reset_url}
        
        此链接将在1小时后失效。如非本人操作，请忽略此邮件。
        
        MediCareAI 智能疾病管理系统
        """

        success = await self.send_email(user.email, subject, html_content, text_content)

        if success:
            return reset_token
        else:
            return None


# 全局邮件服务实例
temail_service = EmailService()
