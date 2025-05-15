from typing import List, Dict, Any, Optional
import asyncio
import httpx
import time
import random
from scholarly import scholarly
import arxiv
from app.core.config import settings
from app.core.logger import get_logger
from app.services.cache_service import cache_service

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

    @staticmethod
    @cache_service.cached(prefix="arxiv_search", ttl=3600)  # 缓存一小时
    async def search_arxiv(query: str, limit: int = 10, sort_by: str = "relevance", categories: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """搜索arXiv"""
        try:
            logger.info(f"搜索arXiv: {query}")

            # 不再需要检查是否启用，因为这是静态方法
            # 处理类别
            if categories:
                category_filter = " AND (" + " OR ".join([f"cat:{cat}" for cat in categories]) + ")"
                query = query + category_filter

            # 处理排序
            if sort_by == "date":
                sort_criterion = arxiv.SortCriterion.SubmittedDate
            else:
                sort_criterion = arxiv.SortCriterion.Relevance

            # 使用更健壮的方式搜索arxiv
            try:
                # 直接使用同步方式搜索，避免使用线程池
                logger.info(f"开始arXiv搜索: {query}, 限制: {limit}")

                # 使用arxiv库搜索
                search = arxiv.Search(
                    query=query,
                    max_results=limit,
                    sort_by=sort_criterion
                )

                # 使用更简单的方式获取结果
                results = []
                for paper in search.results():
                    try:
                        # 提取需要的字段
                        paper_data = {
                            "title": paper.title,
                            "authors": [author.name for author in paper.authors],
                            "year": paper.published.year if hasattr(paper, "published") else "",
                            "abstract": paper.summary,
                            "url": paper.pdf_url,
                            "categories": paper.categories,
                            "source": "arxiv"
                        }
                        results.append(paper_data)

                        # 如果已经获取了足够的结果，就停止
                        if len(results) >= limit:
                            break
                    except Exception as e:
                        logger.error(f"处理arXiv结果时出错: {str(e)}")
                        continue

                logger.info(f"arXiv搜索完成，找到 {len(results)} 条结果")
                return results

            except Exception as e:
                logger.error(f"直接搜索arXiv失败: {str(e)}")

                # 如果直接搜索失败，尝试使用备用方法
                logger.info("尝试使用备用方法搜索arXiv")

                # 使用线程池执行同步操作
                def get_results():
                    try:
                        # 添加随机延迟，避免多个请求同时发送
                        time.sleep(random.uniform(0.5, 2.0))

                        # 重新创建搜索对象
                        backup_search = arxiv.Search(
                            query=query,
                            max_results=limit,
                            sort_by=sort_criterion
                        )

                        # 获取结果
                        return list(backup_search.results())
                    except Exception as e:
                        logger.error(f"arXiv备用方法获取结果失败: {str(e)}")
                        return []

                # 使用run_in_executor替代asyncio.to_thread
                max_retries = 3
                base_delay = 2

                for retry in range(max_retries):
                    try:
                        if retry > 0:
                            # 重试前等待
                            wait_time = base_delay * (1.5 ** retry) + random.uniform(0, 1)
                            logger.info(f"arXiv备用请求前等待 {wait_time:.2f} 秒")
                            await asyncio.sleep(wait_time)

                        loop = asyncio.get_event_loop()
                        search_results = await loop.run_in_executor(None, get_results)

                        if search_results:  # 如果有结果，跳出重试循环
                            break
                        elif retry < max_retries - 1:  # 如果没有结果但还有重试机会
                            logger.warning(f"arXiv备用搜索返回空结果，将重试 ({retry+1}/{max_retries})")
                        else:
                            logger.warning(f"arXiv备用搜索所有重试均返回空结果")
                    except Exception as e:
                        logger.error(f"arXiv备用搜索异常: {str(e)}")
                        if retry < max_retries - 1:
                            wait_time = base_delay * (1.5 ** retry) + random.uniform(0, 1)
                            logger.warning(f"等待 {wait_time:.2f} 秒后重试 ({retry+1}/{max_retries})")
                            await asyncio.sleep(wait_time)
                        else:
                            logger.error(f"arXiv备用搜索失败，所有重试均失败")
                            return []

                results = []
                for result in search_results:
                    try:
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
                    except Exception as e:
                        logger.error(f"处理arXiv备用结果时出错: {str(e)}")
                        continue

                logger.info(f"arXiv备用搜索完成，找到 {len(results)} 条结果")
                return results

        except Exception as e:
            logger.error(f"arXiv搜索失败: {str(e)}")
            # 返回空列表而不是抛出异常
            return []

    @cache_service.cached(prefix="semantic_scholar_search", ttl=3600)  # 缓存一小时
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
            if self.semantic_scholar_api_key and self.semantic_scholar_api_key != "your_semantic_scholar_api_key":
                headers["x-api-key"] = self.semantic_scholar_api_key
                logger.info("Semantic Scholar API使用API密钥")
            else:
                logger.warning("Semantic Scholar API未配置API密钥或使用示例密钥，将使用无密钥访问")

            # 发送请求，带增强的重试和延迟机制
            max_retries = 5  # 增加重试次数
            base_delay = 2  # 初始延迟秒数
            max_delay = 60  # 最大延迟秒数

            for retry in range(max_retries):
                try:
                    # 添加随机延迟，避免多个请求同时发送
                    if retry > 0:
                        # 指数退避与抖动结合
                        delay = min(base_delay * (2 ** retry) + random.uniform(0, 1), max_delay)
                        logger.info(f"Semantic Scholar请求前等待 {delay:.2f} 秒")
                        await asyncio.sleep(delay)

                    # 发送请求
                    response = await self.client.get(url, params=params, headers=headers)
                    response.raise_for_status()
                    data = response.json()

                    # 请求成功，跳出重试循环
                    break

                except httpx.HTTPStatusError as e:
                    status_code = e.response.status_code
                    logger.warning(f"Semantic Scholar请求失败，状态码: {status_code}")

                    if status_code == 429:  # Too Many Requests
                        # 使用更长的延迟
                        wait_time = min(base_delay * (2 ** retry) + random.uniform(0, 5), max_delay)
                        logger.warning(f"Semantic Scholar请求限制，等待 {wait_time:.2f} 秒后重试 ({retry+1}/{max_retries})")
                        await asyncio.sleep(wait_time)
                    elif status_code == 503:  # Service Unavailable
                        # 服务不可用，等待后重试
                        wait_time = min(base_delay * (2 ** retry) + random.uniform(0, 3), max_delay)
                        logger.warning(f"Semantic Scholar服务不可用，等待 {wait_time:.2f} 秒后重试 ({retry+1}/{max_retries})")
                        await asyncio.sleep(wait_time)
                    elif retry < max_retries - 1:  # 其他错误，但还有重试机会
                        wait_time = min(base_delay * (1.5 ** retry) + random.uniform(0, 1), max_delay)
                        logger.warning(f"Semantic Scholar请求错误，等待 {wait_time:.2f} 秒后重试 ({retry+1}/{max_retries})")
                        await asyncio.sleep(wait_time)
                    else:
                        # 最后一次重试也失败，返回空结果
                        logger.error(f"Semantic Scholar请求失败，所有重试均失败: {str(e)}")
                        return []

                except Exception as e:
                    logger.error(f"Semantic Scholar请求异常: {str(e)}")
                    if retry < max_retries - 1:
                        wait_time = min(base_delay * (1.5 ** retry) + random.uniform(0, 1), max_delay)
                        logger.warning(f"等待 {wait_time:.2f} 秒后重试 ({retry+1}/{max_retries})")
                        await asyncio.sleep(wait_time)
                    else:
                        # 最后一次重试也失败，返回空结果
                        logger.error(f"Semantic Scholar请求失败，所有重试均失败: {str(e)}")
                        return []

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

    @cache_service.cached(prefix="academic_papers_search", ttl=3600)  # 缓存一小时
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

            # 优先使用arXiv（不需要API密钥）
            if search_sources.get("arxiv", False):
                logger.info("优先使用arXiv搜索")
                try:
                    # 使用静态方法
                    arxiv_results = await AcademicSearchService.search_arxiv(query, limit, sort_by, categories)

                    # 检查结果是否为列表
                    if not isinstance(arxiv_results, list):
                        logger.warning(f"arXiv搜索返回了非列表结果: {type(arxiv_results)}")
                        arxiv_results = []

                    # 确保结果是可序列化的
                    serializable_results = []
                    for paper in arxiv_results:
                        if not isinstance(paper, dict):
                            logger.warning(f"跳过非字典类型的论文: {type(paper)}")
                            continue

                        try:
                            serializable_paper = {
                                "title": str(paper.get("title", "")) if paper.get("title") is not None else "",
                                "authors": paper.get("authors", []),
                                "year": str(paper.get("year", "")) if paper.get("year") is not None else "",
                                "abstract": str(paper.get("abstract", ""))[:300] if paper.get("abstract") is not None else "",  # 限制摘要长度
                                "url": str(paper.get("url", "")) if paper.get("url") is not None else "",
                                "source": "arxiv"
                            }
                            serializable_results.append(serializable_paper)
                        except Exception as e:
                            logger.error(f"处理arXiv论文数据时出错: {str(e)}")
                            continue

                    if serializable_results:
                        logger.info(f"arXiv搜索成功，找到 {len(serializable_results)} 条结果")
                        return {
                            "results": serializable_results[:limit],
                            "total": len(serializable_results),
                            "query": query,
                            "sources_stats": {"arxiv": len(serializable_results)}
                        }
                    else:
                        logger.warning("arXiv搜索未找到结果，尝试其他来源")
                except Exception as e:
                    logger.error(f"arXiv搜索失败: {str(e)}")
                    # 如果arXiv失败，尝试其他来源

            # 并行搜索多个来源
            tasks = []
            source_names = []

            # 添加Semantic Scholar搜索任务
            if search_sources.get("semantic_scholar", False):
                tasks.append(self.search_semantic_scholar(query, limit, sort_by, years, fields))
                source_names.append("semantic_scholar")

            # 如果前面的arXiv搜索失败，再次尝试
            if search_sources.get("arxiv", False) and not any(t for t in tasks):
                tasks.append(AcademicSearchService.search_arxiv(query, limit, sort_by, categories))
                source_names.append("arxiv")

            # 添加Google Scholar搜索任务
            if search_sources.get("google_scholar", False):
                tasks.append(self.search_google_scholar(query, limit, sort_by, years))
                source_names.append("google_scholar")

            # 如果没有任何搜索任务，返回空结果
            if not tasks:
                logger.warning("没有启用的搜索源，返回空结果")
                return {
                    "results": [],
                    "total": 0,
                    "query": query,
                    "sources_stats": {}
                }

            # 并行执行所有搜索任务
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 合并结果
            all_papers = []
            sources_stats = {}

            # 处理每个搜索源的结果
            for i, result in enumerate(results):
                source_name = source_names[i] if i < len(source_names) else "unknown"

                if isinstance(result, list):
                    # 正常结果
                    sources_stats[source_name] = len(result)
                    all_papers.extend(result)
                elif isinstance(result, Exception):
                    # 异常结果
                    logger.error(f"搜索源 {source_name} 失败: {str(result)}")
                    sources_stats[source_name] = 0
                elif result is None:
                    # 空结果
                    logger.warning(f"搜索源 {source_name} 返回了None")
                    sources_stats[source_name] = 0
                else:
                    # 其他类型的结果
                    logger.error(f"搜索源 {source_name} 返回了非列表结果: {type(result)}")
                    sources_stats[source_name] = 0

            # 去重（基于标题）
            unique_papers = {}
            for paper in all_papers:
                # 跳过非字典类型的论文
                if not isinstance(paper, dict):
                    logger.warning(f"跳过非字典类型的论文: {type(paper)}")
                    continue

                try:
                    title = str(paper.get("title", "")).lower() if paper.get("title") is not None else ""
                    if title and title not in unique_papers:
                        # 确保每个论文对象都是可序列化的
                        serializable_paper = {
                            "title": str(paper.get("title", "")) if paper.get("title") is not None else "",
                            "authors": paper.get("authors", []),
                            "year": str(paper.get("year", "")) if paper.get("year") is not None else "",
                            "abstract": str(paper.get("abstract", ""))[:300] if paper.get("abstract") is not None else "",  # 限制摘要长度
                            "url": str(paper.get("url", "")) if paper.get("url") is not None else "",
                            "source": str(paper.get("source", "unknown")) if paper.get("source") is not None else "unknown"
                        }

                        # 可选字段，如果存在则添加
                        if "citations" in paper and paper["citations"] is not None:
                            serializable_paper["citations"] = int(paper["citations"]) if isinstance(paper["citations"], (int, float)) else 0
                        if "venue" in paper and paper["venue"] is not None:
                            serializable_paper["venue"] = str(paper["venue"])
                        if "categories" in paper and paper["categories"] is not None:
                            serializable_paper["categories"] = paper["categories"]

                        unique_papers[title] = serializable_paper
                except Exception as e:
                    logger.error(f"处理论文数据时出错: {str(e)}")
                    continue

            # 排序
            try:
                if sort_by == "citations":
                    sorted_papers = sorted(
                        unique_papers.values(),
                        key=lambda x: int(x.get("citations", 0)) if x.get("citations") is not None else 0,
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
            except Exception as e:
                logger.error(f"排序论文时出错: {str(e)}")
                sorted_papers = list(unique_papers.values())

            logger.info(f"综合搜索完成，找到 {len(sorted_papers)} 条去重结果")

            # 返回结果
            return {
                "results": sorted_papers[:limit],
                "total": len(sorted_papers),
                "query": query,
                "sources_stats": sources_stats
            }

        except Exception as e:
            logger.error(f"综合搜索失败: {str(e)}")
            # 返回空结果而不是抛出异常
            return {
                "results": [],
                "total": 0,
                "query": query,
                "sources_stats": {}
            }

    @cache_service.cached(prefix="paper_details", ttl=86400)  # 缓存24小时
    async def get_paper_details(self, paper_id: str, source: str = "semantic_scholar") -> Dict[str, Any]:
        """获取论文详情"""
        try:
            logger.info(f"获取论文详情: {paper_id} 来源: {source}")

            if source == "semantic_scholar":
                try:
                    # 构建API请求
                    url = f"{self.semantic_scholar_api_url}/paper/{paper_id}"
                    params = {
                        "fields": self.semantic_scholar_fields
                    }

                    # 添加API密钥
                    headers = {}
                    if self.semantic_scholar_api_key and self.semantic_scholar_api_key != "your_semantic_scholar_api_key":
                        headers["x-api-key"] = self.semantic_scholar_api_key
                        logger.info("Semantic Scholar API使用API密钥")
                    else:
                        logger.warning("Semantic Scholar API未配置API密钥或使用示例密钥，将使用无密钥访问")

                    # 发送请求，带重试和延迟
                    max_retries = 3
                    retry_delay = 2  # 初始延迟秒数

                    paper = None
                    for retry in range(max_retries):
                        try:
                            response = await self.client.get(url, params=params, headers=headers)
                            response.raise_for_status()
                            paper = response.json()
                            break
                        except Exception as e:
                            if retry < max_retries - 1:
                                # 如果是429错误，增加更长的延迟
                                if hasattr(e, 'response') and getattr(e.response, 'status_code', None) == 429:
                                    wait_time = retry_delay * (2 ** retry)  # 指数退避
                                    logger.warning(f"Semantic Scholar请求限制，等待{wait_time}秒后重试")
                                    await asyncio.sleep(wait_time)
                                else:
                                    await asyncio.sleep(retry_delay)
                            else:
                                # 最后一次重试也失败，记录错误并返回空结果
                                logger.error(f"Semantic Scholar获取论文详情失败: {str(e)}")
                                return {}

                    # 检查paper是否为None
                    if paper is None:
                        logger.error("Semantic Scholar返回了空结果")
                        return {}

                    # 确保返回的数据是可序列化的
                    return {
                        "title": str(paper.get("title", "")) if paper.get("title") is not None else "",
                        "authors": [str(author.get("name", "")) for author in paper.get("authors", [])],
                        "year": str(paper.get("year", "")) if paper.get("year") is not None else "",
                        "abstract": str(paper.get("abstract", "")) if paper.get("abstract") is not None else "",
                        "url": str(paper.get("url", "")) if paper.get("url") is not None else "",
                        "venue": str(paper.get("venue", "")) if paper.get("venue") is not None else "",
                        "citations": int(paper.get("citationCount", 0)) if paper.get("citationCount") is not None else 0,
                        "references": paper.get("references", []),
                        "source": "semantic_scholar"
                    }
                except Exception as e:
                    logger.error(f"处理Semantic Scholar论文详情时出错: {str(e)}")
                    return {}

            elif source == "arxiv":
                try:
                    # 使用arxiv库获取详情
                    search = arxiv.Search(id_list=[paper_id])

                    # 直接使用同步方式获取结果
                    try:
                        # 直接获取结果
                        results = list(search.results())
                        if not results:
                            logger.warning(f"arXiv未找到论文: {paper_id}")
                            return {}

                        result = results[0]

                        # 确保返回的数据是可序列化的
                        return {
                            "title": str(result.title) if hasattr(result, "title") else "",
                            "authors": [str(author.name) for author in result.authors] if hasattr(result, "authors") else [],
                            "year": str(result.published.year) if hasattr(result, "published") else "",
                            "abstract": str(result.summary) if hasattr(result, "summary") else "",
                            "url": str(result.pdf_url) if hasattr(result, "pdf_url") else "",
                            "categories": result.categories if hasattr(result, "categories") else [],
                            "source": "arxiv"
                        }
                    except Exception as e:
                        logger.error(f"直接获取arXiv论文详情失败: {str(e)}")

                        # 使用备用方法
                        logger.info("尝试使用备用方法获取arXiv论文详情")

                        # 使用线程池执行同步操作
                        def get_result():
                            try:
                                backup_search = arxiv.Search(id_list=[paper_id])
                                results = list(backup_search.results())
                                if results:
                                    return results[0]
                                return None
                            except Exception as e:
                                logger.error(f"arXiv备用方法获取结果失败: {str(e)}")
                                return None

                        # 使用run_in_executor执行同步操作
                        loop = asyncio.get_event_loop()
                        result = await loop.run_in_executor(None, get_result)

                        if result is None:
                            logger.error(f"arXiv备用方法未找到论文: {paper_id}")
                            return {}

                        # 确保返回的数据是可序列化的
                        return {
                            "title": str(result.title) if hasattr(result, "title") else "",
                            "authors": [str(author.name) for author in result.authors] if hasattr(result, "authors") else [],
                            "year": str(result.published.year) if hasattr(result, "published") else "",
                            "abstract": str(result.summary) if hasattr(result, "summary") else "",
                            "url": str(result.pdf_url) if hasattr(result, "pdf_url") else "",
                            "categories": result.categories if hasattr(result, "categories") else [],
                            "source": "arxiv"
                        }
                except Exception as e:
                    logger.error(f"获取arXiv论文详情失败: {str(e)}")
                    return {}

            else:
                logger.error(f"不支持的来源: {source}")
                return {}

        except Exception as e:
            logger.error(f"获取论文详情失败: {str(e)}")
            return {}

    @cache_service.cached(prefix="research_trends", ttl=86400)  # 缓存24小时
    async def get_research_trends(self, field: str) -> List[Dict[str, Any]]:
        """获取研究趋势"""
        try:
            logger.info(f"获取研究趋势: {field}")

            # 防止返回自身
            if not field or not isinstance(field, str):
                logger.warning(f"研究领域参数无效: {field}, 返回空列表")
                return []

            # 构建查询
            query = f"survey {field} recent advances"
            logger.info(f"研究趋势查询: {query}")

            # 搜索最近的综述论文
            try:
                # 使用更健壮的查询方式
                try:
                    # 尝试使用主要查询
                    search_result = await self.search_academic_papers(
                        query=query,
                        limit=15,  # 获取更多结果以增加筛选后的有效数据
                        sort_by="date",
                        years="last_5"
                    )
                except Exception as search_error:
                    # 记录原始错误
                    logger.error(f"主要研究趋势查询失败: {str(search_error)}")

                    # 降级：使用更简单的查询
                    try:
                        logger.info(f"尝试使用备用查询: {field}")
                        search_result = await self.search_academic_papers(
                            query=field,
                            limit=15,
                            sort_by="relevance"
                        )
                    except Exception as backup_error:
                        logger.error(f"备用研究趋势查询也失败: {str(backup_error)}")
                        # 返回空结果而不是抛出异常
                        return []

                # 验证搜索结果格式
                if not isinstance(search_result, dict) or "results" not in search_result:
                    logger.warning(f"搜索结果格式无效: {type(search_result)}, 返回空列表")
                    return []

                # 检查结果是否为空
                if not search_result["results"]:
                    logger.warning(f"搜索结果为空，返回空列表")
                    return []

                # 按引用次数排序
                try:
                    papers = sorted(
                        search_result["results"],
                        key=lambda x: int(x.get("citations", 0)) if x.get("citations") is not None else 0,
                        reverse=True
                    )
                except Exception as sort_error:
                    logger.error(f"排序论文时出错: {str(sort_error)}")
                    # 如果排序失败，直接使用原始结果
                    papers = search_result["results"]
            except Exception as e:
                logger.error(f"搜索学术论文失败: {str(e)}")
                return []

            # 提取趋势信息，确保所有字段都是可序列化的
            trends = []
            for paper in papers[:10]:
                if not isinstance(paper, dict):
                    logger.warning(f"跳过非字典类型的论文: {type(paper)}")
                    continue

                try:
                    # 确保所有字段都是基本类型
                    trend = {
                        "title": str(paper.get("title", "")) if paper.get("title") is not None else "",
                        "abstract": str(paper.get("abstract", ""))[:300] if paper.get("abstract") is not None else "",  # 限制摘要长度
                        "year": str(paper.get("year", "")) if paper.get("year") is not None else "",
                        "url": str(paper.get("url", "")) if paper.get("url") is not None else "",
                        "citations": int(paper.get("citations", 0)) if paper.get("citations") is not None and str(paper.get("citations", "")).isdigit() else 0
                    }
                    trends.append(trend)
                except Exception as e:
                    logger.error(f"处理论文数据时出错: {str(e)}, 跳过此论文")
                    continue

            logger.info(f"获取研究趋势完成，找到 {len(trends)} 条趋势")

            # 确保返回的是可序列化的列表
            if not isinstance(trends, list):
                logger.warning(f"趋势不是列表类型: {type(trends)}, 返回空列表")
                return []

            return trends

        except Exception as e:
            logger.error(f"获取研究趋势失败: {str(e)}")
            # 返回空列表而不是抛出异常
            return []

# 创建全局学术搜索服务实例
academic_search_service = AcademicSearchService()
