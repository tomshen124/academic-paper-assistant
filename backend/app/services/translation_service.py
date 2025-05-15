from typing import Optional, Dict, Any
from app.core.logger import get_logger
from app.services.llm.llm_service import LLMService
from app.services.llm_service import llm_service
from app.core.config import settings

logger = get_logger("translation")

class TranslationService:
    """翻译服务，用于将内容从一种语言翻译为另一种语言"""

    def __init__(self, default_llm_service: LLMService = None):
        """初始化翻译服务"""
        # 使用传入的LLM服务或全局LLM服务作为默认服务
        self.default_llm_service = default_llm_service or llm_service

        # 检查是否使用默认LLM
        self.use_default_llm = getattr(settings, "translation", {}).get("use_default_llm", True)

        # 如果不使用默认LLM，创建专用LLM服务
        if not self.use_default_llm:
            self.translation_llm_service = self._create_translation_llm_service()
            logger.info("已创建翻译专用LLM服务")
        else:
            self.translation_llm_service = self.default_llm_service
            logger.info("使用默认LLM服务进行翻译")

        logger.info("翻译服务初始化完成")

    def _create_translation_llm_service(self) -> LLMService:
        """创建翻译专用的LLM服务实例"""
        # 创建一个新的LLM服务实例
        translation_llm = LLMService()

        # 记录使用的模型
        translation_config = getattr(settings, "translation", {})
        model = translation_config.get("model")
        if model:
            logger.info(f"翻译服务使用专用模型: {model}")

        return translation_llm

    async def translate(self,
                        content: str,
                        source_lang: str = "en",
                        target_lang: str = "zh-CN",
                        is_academic: bool = True) -> str:
        """
        翻译内容

        Args:
            content: 要翻译的内容
            source_lang: 源语言代码 (默认: "en")
            target_lang: 目标语言代码 (默认: "zh-CN")
            is_academic: 是否为学术内容 (默认: True)

        Returns:
            翻译后的内容
        """
        try:
            if not content or content.strip() == "":
                logger.warning("翻译内容为空")
                return ""

            logger.info(f"翻译内容: {source_lang} -> {target_lang}, 长度: {len(content)}")

            # 构建提示
            system_prompt = self._build_translation_prompt(source_lang, target_lang, is_academic)

            # 确保最后一条消息是用户消息
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ]

            # 获取翻译配置
            translation_config = getattr(settings, "translation", {})
            max_tokens = translation_config.get("max_tokens", len(content) * 2)
            temperature = translation_config.get("temperature", 0.3)

            # 调用LLM
            response = await self.translation_llm_service.acompletion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                task="translate",
                task_type="translation",
                model=translation_config.get("model") if not self.use_default_llm else None,
                agent_type="translation"  # 使用翻译智能体配置
            )

            translated_content = response.choices[0].message.content
            logger.info(f"翻译完成: 原始长度={len(content)}, 翻译后长度={len(translated_content)}")

            return translated_content
        except Exception as e:
            logger.error(f"翻译失败: {str(e)}")
            return f"翻译失败: {str(e)}"

    def _build_translation_prompt(self, source_lang: str, target_lang: str, is_academic: bool) -> str:
        """构建翻译提示"""
        prompt = f"""你是一个专业的翻译专家。请将以下{source_lang}内容翻译成{target_lang}，保持原文的意思和风格。"""

        if is_academic:
            prompt += """
作为学术翻译，请特别注意以下几点：
1. 保持学术术语的准确性和一致性
2. 保留原文的学术风格和论证结构
3. 确保专业名词的翻译符合学科领域的惯例
4. 对于引用和参考文献，保持原有格式
5. 对于图表描述，确保翻译后的描述与图表内容一致
"""

        prompt += """
请只返回翻译后的内容，不要添加任何解释、注释或标记。不要在回复中包含"翻译如下"或"以下是翻译"等引导语。
"""

        return prompt

    async def batch_translate(self, items: list, content_key: str,
                             source_lang: str = "en", target_lang: str = "zh-CN",
                             is_academic: bool = True) -> list:
        """
        批量翻译列表中的内容

        Args:
            items: 要翻译的项目列表
            content_key: 内容字段的键名
            source_lang: 源语言代码
            target_lang: 目标语言代码
            is_academic: 是否为学术内容

        Returns:
            翻译后的项目列表
        """
        try:
            logger.info(f"批量翻译 {len(items)} 个项目: {source_lang} -> {target_lang}")

            translated_items = []
            for item in items:
                if not item or content_key not in item:
                    translated_items.append(item)
                    continue

                content = item[content_key]
                if not content:
                    translated_items.append(item)
                    continue

                # 构建提示
                system_prompt = self._build_translation_prompt(source_lang, target_lang, is_academic)

                # 确保最后一条消息是用户消息
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": content}
                ]

                # 获取翻译配置
                translation_config = getattr(settings, "translation", {})
                max_tokens = translation_config.get("max_tokens", len(content) * 2)
                temperature = translation_config.get("temperature", 0.3)

                # 调用LLM
                response = await self.translation_llm_service.acompletion(
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    task="batch_translate",
                    task_type="translation",
                    model=translation_config.get("model") if not self.use_default_llm else None,
                    agent_type="translation"  # 使用翻译智能体配置
                )

                translated_content = response.choices[0].message.content

                # 创建新项目，避免修改原始项目
                translated_item = dict(item)
                translated_item[content_key] = translated_content
                translated_items.append(translated_item)

            logger.info(f"批量翻译完成: {len(translated_items)} 个项目")
            return translated_items
        except Exception as e:
            logger.error(f"批量翻译失败: {str(e)}")
            return items
