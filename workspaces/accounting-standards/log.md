# 操作日志 — accounting-standards

## [2026-09-18] deepen | 收入四项子专题
- 依据：本地第14号收入准则第15至16条、第24至25条、第34条、第41至42条；财政部公开的可变对价、主要责任人和代理人、合同负债案例及实施问答。
- 更新：`wiki/concepts/revenue.md`、`wiki/sources/cas_14_revenue.md`、`wiki/indexes/practice_cases_index.md`。
- 状态：四项子专题已形成有条款引用的初步判断框架；官方案例和问答目前通过在线链接引用，尚未逐篇保存为本地原文。

## [2026-09-18] catalog | 准则补充资料状态核对
- 新建：`wiki/indexes/supplementary_materials_index.md`，登记本地 27 份 2006 年应用指南（含第12号重复件）、解释第1至20号及财政部官方问答和案例入口。
- 核对：第15号与新收入准则衔接依据；解释部分本地文件仅有印发通知；第30号 2026 年修订及分步施行日期。
- 更新：准则体系索引、首页、收入、建造合同、财务报表列报概念页及第30号来源摘要。
- 待续：补齐解释附件原文，逐篇摄入财政部问答与应用案例，并逐项核对后续修订的应用指南。

## [2026-08-29] ingest | 企业会计准则第15号建造合同
- 来源：`raw/papers/standards/01_企业会计准则_财政部/企业会计准则第15号-建造合同.md`
- 清理：删除原始 Markdown 末尾混入的“使用说明”和“应用指南 Markdown”提示，保留准则正文与适用状态提示。
- 新建：`wiki/sources/cas_15_construction_contracts.md`、`wiki/concepts/construction_contracts.md`
- 更新：`wiki/indexes/standards_system_index.md`、`wiki/indexes/topics_index.md`、`wiki/indexes/practice_cases_index.md`、`wiki/indexes/regulation_disclosure_index.md`、`wiki/root_index.md`
- 摘要：第15号已按“建造合同”为顶层概念、“企业会计准则第15号：建造合同”为来源摘要的结构接入知识库。

## [2026-08-28] refactor | 顶层概念收敛到准则标题 AA
- 删除：`wiki/concepts/revenue_recognition.md`
- 更新：`wiki/concepts/revenue.md`、`wiki/concepts/financial_instruments.md`、`wiki/sources/cas_14_revenue.md`、`wiki/indexes/standards_system_index.md`、`wiki/indexes/topics_index.md`、`wiki/indexes/regulation_disclosure_index.md`、`wiki/root_index.md`
- 摘要：顶层概念页只对应“企业会计准则第XX号——AA”中的 AA；“收入确认”改为“收入”页内的子专题，不再与“收入”平级；第22号概念标题收敛为“金融工具确认和计量”。

## [2026-08-28] refactor | 准则来源层与专业概念层分离
- 新建：37 个准则来源摘要页，补齐基本准则及第1号至第42号中当前资料目录可对应的来源层页面。
- 新建：37 个专业概念页，包括存货、长期股权投资、投资性房地产、固定资产、无形资产、资产减值、所得税、企业合并、财务报表列报、公允价值计量等。
- 删除：上一轮生成的 `wiki/concepts/cas_*.md` 准则入口概念页。
- 更新：`wiki/indexes/standards_system_index.md`、`wiki/indexes/topics_index.md`、`wiki/indexes/practice_cases_index.md`、`wiki/indexes/regulation_disclosure_index.md`、`wiki/root_index.md`
- 摘要：准则文件统一进入 `wiki/sources/`，专业知识统一进入 `wiki/concepts/`，避免“准则名称”和“会计概念”混在同一层。

## [2026-08-28] refactor | 收入概念层级样板
- 新建：`wiki/concepts/revenue.md`
- 更新：`wiki/concepts/revenue_recognition.md`、`wiki/sources/cas_14_revenue.md`、`wiki/indexes/standards_system_index.md`、`wiki/indexes/topics_index.md`、`wiki/root_index.md`
- 删除：`wiki/concepts/cas_14_revenue.md`
- 摘要：将“收入”设为主概念，“收入确认”设为收入的一部分，“企业会计准则第14号：收入”保留为来源摘要，避免把准则文件误当成专业概念。

## [2026-08-28] framework | 补齐企业会计准则入口
- 来源：`raw/papers/standards/01_企业会计准则_财政部/*.md`
- 新建：基本准则及第1号至第42号准则入口页，共 42 个；第15号建造合同当前资料目录未见单独原文，先在索引中列为待补资料。
- 更新：`wiki/indexes/standards_system_index.md`、`wiki/indexes/topics_index.md`、`wiki/indexes/regulation_disclosure_index.md`、`wiki/root_index.md`
- 摘要：将企业会计准则知识库从 5 个高频主题扩展为完整准则入口框架，后续可逐项深读应用指南、解释公告和案例。

## [2026-08-28] ingest | 首批企业会计准则原文
- 来源：`raw/papers/standards/01_企业会计准则_财政部/015_企业会计准则第14号——收入.md`、`021_企业会计准则第21号——租赁.md`、`022_企业会计准则第22号——金融工具确认和计量（财会〔2017〕7号）.md`、`038_企业会计准则第33号——合并财务报表.md`、`041_企业会计准则第36号——关联方披露.md`
- 新建：`wiki/sources/cas_14_revenue.md`、`wiki/sources/cas_21_lease.md`、`wiki/sources/cas_22_financial_instruments_2017.md`、`wiki/sources/cas_33_consolidated_financial_statements.md`、`wiki/sources/cas_36_related_party_disclosure.md`
- 更新：`wiki/concepts/revenue_recognition.md`、`wiki/concepts/lease_accounting.md`、`wiki/concepts/financial_instruments.md`、`wiki/concepts/consolidated_financial_statements.md`、`wiki/concepts/related_party_disclosure.md`
- 标记待更新：上述 5 个主题页均保留应用指南、监管问答和案例材料的后续补充标记。
- MOC：`wiki/root_index.md`、`wiki/indexes/practice_cases_index.md`
- 摘要：首批把收入、租赁、金融工具、合并报表和关联方披露从占位页升级为有准则原文引用的核心知识页。

- 2026-08-28: 初始化企业会计准则知识库，建立首页、准则体系、重点科目、监管披露和实务案例分类框架。
## [2026-08-28] human | 创建 workspace
- 由 `python scripts/k.py new-workspace accounting-standards` 脚手架生成

## [2026-09-18] ingest | 财政部实施问答、应用案例和其他规定
- 来源：财政部会计司官方三个栏目，抓取 169 篇；保存原始网页及 PDF 附件至 `raw/articles/mof/`。
- 转换：168 篇通过正文非空和附件文字提取检查，转换成带锚点的本地 Markdown；保留 1 篇扫描 PDF 待 OCR（《增值税会计处理规定》通知），其网页正文已保存。
- 新建：168 个 `wiki/sources/mof_*.md` 来源页及 `wiki/indexes/mof_official_materials_index.md` 总目录。
- 更新：将相关来源链接到 23 个现有顶层概念页；PPP 专项材料保留于总目录，未强行归入“收入”。“收入”页四个子专题的案例与问答引用改为本地来源页。
- 检索：来源页在搜索时联查本地转换正文，可搜索附件内的词语；新增回归测试。来源页为草稿，尚未逐篇形成专业章节摘要。
## [2026-09-18] expand | 补齐概念页的准则基础框架
- 更新：37 个含 `## 待补充` 的概念页，改为按准则原文组织的定义与适用范围、确认与计量要点、列报与披露、实务复核、案例与资料边界。
- 引用：新增条文块级锚点；对条文中的条件清单按本地原文节录，保留点击核对入口。
- 版本：第30号财务报表列报注明2026年修订版分阶段施行；第26号再保险合同注明须核对新保险合同准则适用。
- 边界：本轮补的是准则基础框架，并非逐篇专业审阅或上市公司问询、处罚、年报案例全覆盖；仍保留草稿和待更新标记。健康度规则和页面未修改。
## [2026-09-19] ingest | 实务汇编 V12 与更新记录（初步登记）
- 两份原始 PDF 保留在本地 raw；V12 已按 PDF 页码转换 2,238 页，更新记录已转换但表格有错列。
- 新建来源页并接入补充资料索引；未复制内部汇编正文到公开 wiki，未逐章核对或据此改写概念结论。
- 注册会计师法两份 PDF 目前位于本库 raw，目标审计法规库尚无原件；未在目标库建立来源页。
