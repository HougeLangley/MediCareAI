"""
Unified Knowledge Base Service
统一知识库服务 - 支持扁平化知识库结构

新架构：所有文档统一存放在 unified/ 目录下，不再按疾病分类
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class UnifiedDocument:
    """统一知识库文档"""
    filename: str
    title: str
    category: str
    tags: List[str] = field(default_factory=list)
    source: str = ""
    content: str = ""
    file_path: Path = None
    file_size: int = 0
    last_modified: datetime = None


class UnifiedKnowledgeLoader:
    """
    统一知识库加载器 (Unified Knowledge Base Loader)
    
    特点：
    - 所有文档存放在 unified/ 目录下
    - 通过 metadata.json 管理文档元数据
    - 支持动态扫描目录自动发现新文档
    - 不再按疾病分类，完全扁平化
    """
    
    def __init__(self, kb_root: str = "/app/data/knowledge_bases"):
        self.kb_root = Path(kb_root)
        self.unified_root = self.kb_root / "unified"
        self.metadata_file = self.unified_root / "metadata.json"
        self._cache: Dict[str, UnifiedDocument] = {}
        self._metadata: Dict = {}
        
        # 确保目录存在
        self.unified_root.mkdir(parents=True, exist_ok=True)
        
        # 加载或创建元数据
        self._load_or_create_metadata()
    
    def _load_or_create_metadata(self):
        """加载或创建元数据文件"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self._metadata = json.load(f)
                logger.info(f"✅ 加载统一知识库元数据: {len(self._metadata.get('documents', []))} 个文档")
            except Exception as e:
                logger.error(f"❌ 加载元数据失败: {e}")
                self._create_default_metadata()
        else:
            self._create_default_metadata()
    
    def _create_default_metadata(self):
        """创建默认元数据"""
        self._metadata = {
            "name": "统一医学知识库",
            "name_en": "Unified Medical Knowledge Base",
            "description": "包含所有医学领域的诊疗指南和知识文档",
            "version": "2.0.0",
            "structure": "unified",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "documents": [],
            "stats": {
                "total_documents": 0,
                "categories": []
            }
        }
        self._save_metadata()
    
    def _save_metadata(self):
        """保存元数据到文件"""
        try:
            self._metadata['updated_at'] = datetime.now().isoformat()
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self._metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ 保存元数据失败: {e}")
    
    def scan_and_update_metadata(self) -> Dict[str, Any]:
        """
        扫描目录并更新元数据
        自动发现新添加的文档
        """
        discovered_docs = []
        categories = set()
        
        # 扫描所有 .md 文件
        for md_file in self.unified_root.glob("*.md"):
            filename = md_file.name
            
            # 检查是否已在元数据中
            existing = next(
                (d for d in self._metadata.get('documents', []) if d['filename'] == filename),
                None
            )
            
            if existing:
                # 更新文件信息
                existing['file_size'] = md_file.stat().st_size
                discovered_docs.append(existing)
                categories.add(existing.get('category', 'uncategorized'))
            else:
                # 新文档 - 自动提取信息
                try:
                    content = md_file.read_text(encoding='utf-8')[:500]  # 读取前500字符
                    
                    # 尝试从内容提取标题（第一行）
                    title = content.split('\n')[0].replace('#', '').strip()
                    if not title:
                        title = filename.replace('.md', '')
                    
                    # 自动推断分类（从文件名或内容）
                    category = self._infer_category(filename, content)
                    categories.add(category)
                    
                    new_doc = {
                        "filename": filename,
                        "title": title,
                        "category": category,
                        "tags": self._extract_tags(filename, content),
                        "source": "",
                        "file_size": md_file.stat().st_size,
                        "added_at": datetime.now().isoformat()
                    }
                    discovered_docs.append(new_doc)
                    logger.info(f"📄 发现新文档: {filename} (分类: {category})")
                    
                except Exception as e:
                    logger.error(f"❌ 处理文档失败 {filename}: {e}")
        
        # 更新元数据
        self._metadata['documents'] = discovered_docs
        self._metadata['stats'] = {
            "total_documents": len(discovered_docs),
            "categories": list(categories),
            "last_scan": datetime.now().isoformat()
        }
        self._save_metadata()
        
        logger.info(f"✅ 扫描完成: {len(discovered_docs)} 个文档, {len(categories)} 个分类")
        return self._metadata['stats']
    
    def _infer_category(self, filename: str, content: str) -> str:
        """
        分类推断 - 统一使用 'unified'
        
        为了简化知识库结构，所有文档统一归类为 'unified'，
        不再按疾病类型细分。分类信息仅用于标识，不影响检索逻辑。
        """
        # 统一使用 'unified' 分类，不再推断具体疾病分类
        return 'unified'
    
    def _extract_tags(self, filename: str, content: str) -> List[str]:
        """从文件名和内容提取标签"""
        tags = []
        text = (filename + ' ' + content[:500]).lower()
        
        tag_keywords = {
            '指南': ['指南', 'guideline', '诊疗'],
            '规范': ['规范', 'standard', '规范化'],
            '儿童': ['儿童', '小儿', 'pediatric', 'children'],
            '急性': ['急性', 'acute'],
            '慢性': ['慢性', 'chronic'],
            '诊断': ['诊断', 'diagnosis', '诊断标准'],
            '治疗': ['治疗', 'therapy', 'treatment', '药物']
        }
        
        for tag, keywords in tag_keywords.items():
            if any(kw in text for kw in keywords):
                tags.append(tag)
        
        return tags[:5]  # 最多5个标签
    
    def list_documents(self, category: str = None) -> List[Dict]:
        """列出所有文档"""
        docs = self._metadata.get('documents', [])
        
        if category:
            docs = [d for d in docs if d.get('category') == category]
        
        return docs
    
    def load_document(self, filename: str) -> Optional[UnifiedDocument]:
        """加载指定文档内容"""
        # 检查缓存
        if filename in self._cache:
            return self._cache[filename]
        
        # 查找文档
        doc_meta = next(
            (d for d in self._metadata.get('documents', []) if d['filename'] == filename),
            None
        )
        
        if not doc_meta:
            return None
        
        file_path = self.unified_root / filename
        if not file_path.exists():
            return None
        
        try:
            content = file_path.read_text(encoding='utf-8')
            stat = file_path.stat()
            
            doc = UnifiedDocument(
                filename=filename,
                title=doc_meta.get('title', filename),
                category=doc_meta.get('category', 'general'),
                tags=doc_meta.get('tags', []),
                source=doc_meta.get('source', ''),
                content=content,
                file_path=file_path,
                file_size=stat.st_size,
                last_modified=datetime.fromtimestamp(stat.st_mtime)
            )
            
            # 缓存
            self._cache[filename] = doc
            return doc
            
        except Exception as e:
            logger.error(f"❌ 读取文档失败 {filename}: {e}")
            return None
    
    def load_all_documents(self) -> List[UnifiedDocument]:
        """加载所有文档"""
        docs = []
        for doc_meta in self._metadata.get('documents', []):
            doc = self.load_document(doc_meta['filename'])
            if doc:
                docs.append(doc)
        return docs
    
    def add_document(self, filename: str, content: str, 
                     title: str = None, category: str = None,
                     tags: List[str] = None, source: str = "") -> bool:
        """
        添加新文档到知识库
        """
        try:
            file_path = self.unified_root / filename
            
            # 写入文件
            file_path.write_text(content, encoding='utf-8')
            
            # 推断元数据
            if not title:
                title = filename.replace('.md', '')
            if not category:
                category = self._infer_category(filename, content)
            if not tags:
                tags = self._extract_tags(filename, content)
            
            # 添加到元数据
            new_doc = {
                "filename": filename,
                "title": title,
                "category": category,
                "tags": tags,
                "source": source,
                "file_size": len(content.encode('utf-8')),
                "added_at": datetime.now().isoformat()
            }
            
            # 检查是否已存在
            existing_idx = next(
                (i for i, d in enumerate(self._metadata['documents']) 
                 if d['filename'] == filename),
                None
            )
            
            if existing_idx is not None:
                self._metadata['documents'][existing_idx] = new_doc
            else:
                self._metadata['documents'].append(new_doc)
            
            # 更新统计
            categories = set(d.get('category', 'general') for d in self._metadata['documents'])
            self._metadata['stats'] = {
                "total_documents": len(self._metadata['documents']),
                "categories": list(categories),
                "last_updated": datetime.now().isoformat()
            }
            
            self._save_metadata()
            
            # 清除缓存
            if filename in self._cache:
                del self._cache[filename]
            
            logger.info(f"✅ 文档已添加: {filename} (分类: {category})")
            return True
            
        except Exception as e:
            logger.error(f"❌ 添加文档失败: {e}")
            return False
    
    def delete_document(self, filename: str) -> bool:
        """删除文档"""
        try:
            file_path = self.unified_root / filename
            
            # 删除文件
            if file_path.exists():
                file_path.unlink()
            
            # 从元数据移除
            self._metadata['documents'] = [
                d for d in self._metadata['documents'] 
                if d['filename'] != filename
            ]
            
            # 更新统计
            categories = set(d.get('category', 'general') for d in self._metadata['documents'])
            self._metadata['stats'] = {
                "total_documents": len(self._metadata['documents']),
                "categories": list(categories),
                "last_updated": datetime.now().isoformat()
            }
            
            self._save_metadata()
            
            # 清除缓存
            if filename in self._cache:
                del self._cache[filename]
            
            logger.info(f"✅ 文档已删除: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 删除文档失败: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        return self._metadata.get('stats', {
            "total_documents": 0,
            "categories": []
        })


# 全局实例（类似原来的 get_knowledge_loader）
_unified_loader: Optional[UnifiedKnowledgeLoader] = None


def get_unified_knowledge_loader(kb_root: str = "/app/data/knowledge_bases") -> UnifiedKnowledgeLoader:
    """获取统一知识库加载器全局实例"""
    global _unified_loader
    if _unified_loader is None:
        _unified_loader = UnifiedKnowledgeLoader(kb_root)
    return _unified_loader
