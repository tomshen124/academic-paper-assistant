from typing import List, Dict, Any, Optional
import asyncio
import httpx
from scholarly import scholarly
import arxiv
from app.core.config import settings
from app.core.logger import get_logger

# 创建日志器
logger = get_logger("academic_search")

class AcademicSearchService:
    """学术搜索服务，用于搜索和获取学术文献"""

    def __init__(self):
        """初始化学术搜索服务"""
        self.client = httpx.AsyncClient(timeout=30.0)

        # 从配置中加载设置
        self.config = settings.get('academic_search', {})
        self.enabled_sources = self.config.get("enabled_sources", {
            "semantic_scholar": True,
            "arxiv": True,
            "google_scholar": False
        })
        self.default_params = self.config.get("default_params", {
            "limit": 10,
            "sort_by": "relevance",
            "years": "all"
        })

        # Semantic Scholar配置
        self.semantic_scholar_config = self.config.get("semantic_scholar", {})
        self.semantic_scholar_api_url = self.semantic_scholar_config.get(
            "api_url", "https://api.semanticscholar.org/graph/v1"
        )
        self.semantic_scholar_fields = self.semantic_scholar_config.get(
            "fields", "title,authors,year,abstract,url,venue,citationCount,references"
        )
        self.use_semantic_scholar_api_key = self.semantic_scholar_config.get("use_api_key", True)
        self.semantic_scholar_api_key = settings.SEMANTIC_SCHOLAR_API_KEY if self.use_semantic_scholar_api_key else None

        # arXiv配置
        self.arxiv_config = self.config.get("arxiv", {})
        self.arxiv_sort_by = self.arxiv_config.get("sort_by", "relevance")
        self.arxiv_categories = self.arxiv_config.get("categories", [])

        # Google Scholar配置
        self.google_scholar_config = self.config.get("google_scholar", {})
        self.google_scholar_proxy = self.google_scholar_config.get("proxy", "")
        self.google_scholar_timeout = self.google_scholar_config.get("timeout", 30)

        logger.info("学术搜索服务初始化完成")

    async def search_google_scholar(self, query: str, limit: int = 10, sort_by: str = "relevance", years: str = "all") -> List[Dict[str, Any]]:
        """搜索Google Scholar"""
        try:
            logger.info(f"搜索Google Scholar: {query}")

            # 检查是否启用
            if not self.enabled_sources.get("google_scholar", False):
                logger.info("Google Scholar搜索已禁用")
                return []

            # 设置代理（如果配置了）
            if self.google_scholar_proxy:
                scholarly.use_proxy(proxy=self.google_scholar_proxy, timeout=self.google_scholar_timeout)

            # 使用scholarly库搜索Google Scholar
            # 注意：这是同步操作，可能会阻塞
            search_query = scholarly.search_pubs(query)
            results = []

            # 获取指定数量的结果
            for _ in range(limit):
                try:
                    publication = next(search_query)
                    # 提取需要的字段
                    result = {
                        "title": publication.get("bib", {}).get("title", ""),
                        "authors": publication.get("bib", {}).get("author", []),
                        "year": publication.get("bib", {}).get("pub_year", ""),
                        "venue": publication.get("bib", {}).get("venue", ""),
                        "abstract": publication.get("bib", {}).get("abstract", ""),
                        "url": publication.get("pub_url", ""),
                        "citations": publication.get("num_citations", 0),
                        "source": "google_scholar"
                    }

                    # 年份过滤
                    if years == "last_1" and result["year"] and int(result["year"]) < 2023:
                        continue
                    elif years == "last_5" and result["year"] and int(result["year"]) < 2019:
                        continue
                    elif years == "last_10" and result["year"] and int(result["year"]) < 2014:
                        continue

                    results.append(result)
                except StopIteration:
                    break
                except Exception as e:
                    logger.error(f"处理Google Scholar结果时出错: {str(e)}")

            # 排序
            if sort_by == "citations":
                results.sort(key=lambda x: x.get("citations", 0), reverse=True)
            elif sort_by == "date" and all(r.get("year") for r in results):
                results.sort(key=lambda x: int(x.get("year", 0)), reverse=True)

            logger.info(f"Google Scholar搜索完成，找到 {len(results)} 条结果")
            return results

        except Exception as e:
            logger.error(f"Google Scholar搜索失败: {str(e)}")
            return []

    async def search_arxiv(self, query: str, limit: int = 10, sort_by: str = "relevance", categories: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """搜索arXiv"""
        try:
            logger.info(f"搜索arXiv: {query}")

            # 检查是否启用
            if not self.enabled_sources.get("arxiv", True):
                logger.info("arXiv搜索已禁用")
                return []

            # 处理类别
            if categories:
                category_filter = " AND (" + " OR ".join([f"cat:{cat}" for cat in categories]) + ")"
                query = query + category_filter
            elif self.arxiv_categories:
                category_filter = " AND (" + " OR ".join([f"cat:{cat}" for cat in self.arxiv_categories]) + ")"
                query = query + category_filter

            # 处理排序
            if sort_by == "date":
                sort_criterion = arxiv.SortCriterion.SubmittedDate
            else:
                sort_criterion = arxiv.SortCriterion.Relevance

            # 使用arxiv库搜索
            search = arxiv.Search(
                query=query,
                max_results=limit,
                sort_by=sort_criterion
            )

            results = []
            for result in await asyncio.to_thread(list, search.results()):
                # 提取需要的字段
                paper = {
                    "title": result.title,
                    "authors": [author.name for author in result.authors],
                    "year": result.published.year if hasattr(result, "published") else "",
                    "abstract": result.summary,
                    "url": result.pdf_url,
                    "categories": result.categories,
                    "source": "arxiv"
                }
                results.append(paper)

            logger.info(f"arXiv搜索完成，找到 {len(results)} 条结果")
            return results

        except Exception as e:
            logger.error(f"arXiv搜索失败: {str(e)}")
            return []

    async def search_semantic_scholar(self, query: str, limit: int = 10, sort_by: str = "relevance", years: str = "all", fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """搜索Semantic Scholar"""
        try:
            logger.info(f"搜索Semantic Scholar: {query}")

            # 检查是否启用
            if not self.enabled_sources.get("semantic_scholar", True):
                logger.info("Semantic Scholar搜索已禁用")
                return []

            # 构建API请求
            url = f"{self.semantic_scholar_api_url}/paper/search"

            # 处理字段
            if fields:
                fields_str = ",".join(fields)
            else:
                fields_str = self.semantic_scholar_fields

            # 处理排序
            if sort_by == "citations":
                sort = "citationCount:desc"
            elif sort_by == "date":
                sort = "year:desc"
            else:
                sort = "relevance"

            # 处理年份过滤
            year_filter = ""
            if years == "last_1":
                year_filter = "&year>=2023"
            elif years == "last_5":
                year_filter = "&year>=2019"
            elif years == "last_10":
                year_filter = "&year>=2014"

            params = {
                "query": query + year_filter,
                "limit": limit,
                "fields": fields_str,
                "sort": sort
            }

            # 添加API密钥
            headers = {}
            if self.semantic_scholar_api_key:
                headers["x-api-key"] = self.semantic_scholar_api_key

            # 发送请求
            response = await self.client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

            # 处理结果
            results = []
            for paper in data.get("data", []):
                result = {
                    "title": paper.get("title", ""),
                    "authors": [author.get("name", "") for author in paper.get("authors", [])],
                    "year": paper.get("year", ""),
                    "abstract": paper.get("abstract", ""),
                    "url": paper.get("url", ""),
                    "venue": paper.get("venue", ""),
                    "citations": paper.get("citationCount", 0),
                    "source": "semantic_scholar"
                }
                results.append(result)

            logger.info(f"Semantic Scholar搜索完成，找到 {len(results)} 条结果")
            return results

        except Exception as e:
            logger.error(f"Semantic Scholar搜索失败: {str(e)}")
            return []

    async def search_academic_papers(
        self,
        query: str,
        limit: int = None,
        sources: Optional[List[str]] = None,
        sort_by: str = None,
        years: str = None,
        categories: Optional[List[str]] = None,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """综合搜索学术论文"""
        try:
            # 使用默认参数（如果未指定）
            if limit is None:
                limit = self.default_params.get("limit", 10)
            if sort_by is None:
                sort_by = self.default_params.get("sort_by", "relevance")
            if years is None:
                years = self.default_params.get("years", "all")

            logger.info(f"综合搜索学术论文: {query}, 限制: {limit}, 排序: {sort_by}, 年份: {years}")

            # 确定要使用的搜索源
            search_sources = {}
            if sources:
                for source in sources:
                    if source in self.enabled_sources and self.enabled_sources[source]:
                        search_sources[source] = True
            else:
                search_sources = self.enabled_sources

            # 并行搜索多个来源
            tasks = []
            if search_sources.get("semantic_scholar", False):
                tasks.append(self.search_semantic_scholar(query, limit, sort_by, years, fields))
            if search_sources.get("arxiv", False):
                tasks.append(self.search_arxiv(query, limit, sort_by, categories))
            if search_sources.get("google_scholar", False):
                tasks.append(self.search_google_scholar(query, limit, sort_by, years))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 合并结果
            all_papers = []
            sources_stats = {}

            for i, result in enumerate(results):
                if isinstance(result, list):
                    source_name = list(search_sources.keys())[i] if i < len(search_sources) else "unknown"
                    sources_stats[source_name] = len(result)
                    all_papers.extend(result)
                else:
                    logger.error(f"搜索失败: {str(result)}")
                    source_name = list(search_sources.keys())[i] if i < len(search_sources) else "unknown"
                    sources_stats[source_name] = 0

            # 去重（基于标题）
            unique_papers = {}
            for paper in all_papers:
                title = paper.get("title", "").lower()
                if title and title not in unique_papers:
                    unique_papers[title] = paper

            # 排序
            if sort_by == "citations":
                sorted_papers = sorted(
                    unique_papers.values(),
                    key=lambda x: x.get("citations", 0),
                    reverse=True
                )
            elif sort_by == "date":
                sorted_papers = sorted(
                    unique_papers.values(),
                    key=lambda x: int(x.get("year", 0)) if x.get("year") and str(x.get("year", "")).isdigit() else 0,
                    reverse=True
                )
            else:
                # 默认按相关性排序（保持原顺序）
                sorted_papers = list(unique_papers.values())

            logger.info(f"综合搜索完成，找到 {len(sorted_papers)} 条去重结果")

            return {
                "results": sorted_papers[:limit],
                "total": len(sorted_papers),
                "query": query,
                "sources_stats": sources_stats
            }

        except Exception as e:
            logger.error(f"综合搜索失败: {str(e)}")
            return {
                "results": [],
                "total": 0,
                "query": query,
                "sources_stats": {}
            }

    async def get_paper_details(self, paper_id: str, source: str = "semantic_scholar") -> Dict[str, Any]:
        """获取论文详情"""
        try:
            logger.info(f"获取论文详情: {paper_id} 来源: {source}")

            if source == "semantic_scholar":
                # 构建API请求
                url = f"{self.semantic_scholar_api_url}/paper/{paper_id}"
                params = {
                    "fields": self.semantic_scholar_fields
                }

                # 添加API密钥
                headers = {}
                if self.semantic_scholar_api_key:
                    headers["x-api-key"] = self.semantic_scholar_api_key

                # 发送请求
                response = await self.client.get(url, params=params, headers=headers)
                response.raise_for_status()
                paper = response.json()

                return {
                    "title": paper.get("title", ""),
                    "authors": [author.get("name", "") for author in paper.get("authors", [])],
                    "year": paper.get("year", ""),
                    "abstract": paper.get("abstract", ""),
                    "url": paper.get("url", ""),
                    "venue": paper.get("venue", ""),
                    "citations": paper.get("citationCount", 0),
                    "references": paper.get("references", []),
                    "source": "semantic_scholar"
                }

            elif source == "arxiv":
                # 使用arxiv库获取详情
                search = arxiv.Search(id_list=[paper_id])
                result = list(search.results())[0]

                return {
                    "title": result.title,
                    "authors": [author.name for author in result.authors],
                    "year": result.published.year if hasattr(result, "published") else "",
                    "abstract": result.summary,
                    "url": result.pdf_url,
                    "categories": result.categories,
                    "source": "arxiv"
                }

            else:
                logger.error(f"不支持的来源: {source}")
                return {}

        except Exception as e:
            logger.error(f"获取论文详情失败: {str(e)}")
            return {}

    async def get_research_trends(self, field: str) -> List[Dict[str, Any]]:
        """获取研究趋势"""
        try:
            logger.info(f"获取研究趋势: {field}")

            # 构建查询
            query = f"survey {field} recent advances"

            # 搜索最近的综述论文
            search_result = await self.search_academic_papers(
                query=query,
                limit=10,
                sort_by="date",
                years="last_5"
            )

            # 按引用次数排序
            papers = sorted(
                search_result["results"],
                key=lambda x: x.get("citations", 0),
                reverse=True
            )

            # 提取趋势信息
            trends = []
            for paper in papers[:10]:
                trend = {
                    "title": paper.get("title", ""),
                    "abstract": paper.get("abstract", ""),
                    "year": paper.get("year", ""),
                    "url": paper.get("url", ""),
                    "citations": paper.get("citations", 0)
                }
                trends.append(trend)

            logger.info(f"获取研究趋势完成，找到 {len(trends)} 条趋势")
            return trends

        except Exception as e:
            logger.error(f"获取研究趋势失败: {str(e)}")
            return []

# 创建全局学术搜索服务实例
academic_search_service = AcademicSearchService()
