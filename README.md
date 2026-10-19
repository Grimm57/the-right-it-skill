# right-it-check · The Right It Skill

> 先确保你在构建「正确的它」，再确保你能把它构建正确。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-8A2BE2.svg)

把 [Alberto Savoia](https://www.albertosavoia.com/)《**做对产品**》（*The Right It*）的整套方法论，封装成一个可以被 AI agent 自动加载并跑完的 [Claude Code](https://claude.com/claude-code) Skill。

它回答的问题只有一个：**这个创意值不值得投入构建？** —— 而不是「怎么把它做出来」。

---

## 为什么需要它

大多数新产品失败，不是因为团队不会做，而是因为**做的是市场不想要的东西**。市场失败律（Law of Market Failure）不会因为你聪明、团队强、市场大就网开一面。

这本书给的答案是：**在投入构建之前，先用预型（pretotype）花几百块、几天时间把市场反应买回来。** 这个 skill 把这套流程固化成了 6 个阶段，agent 可以一步步带你跑完：

| 阶段 | 产出 |
|---|---|
| 0 · 摄入 | 创意、目标市场、期望反应、已有证据 |
| 1 · 清晰化 | MEH → XYZ 假说（**至少 X% 的 Y 会 Z**）→ 拆成 2～4 个可测的 xyz |
| 2 · 证据审计 | 用**切身利益卡尺**把手上的「证据」折算成点数 |
| 3 · 试验设计 | 选预型技术，按 **DTD / HTD / $TD** 排序 |
| 4 · 物料生成 | 落地页、广告文案、分镜脚本、记录表……可直接投放 |
| 5 · 判定 | **TRI 计量仪**：5 级刻度 + 试验次数校验 |
| 6 · 决策 | **争取它 / 调整它 / 放弃它** |

## 核心判定逻辑

**切身利益卡尺（Skin-in-the-Game Lens）** —— 判断「证据」的含金量：

| 证据 | 点数 |
|---|---|
| 意见、点赞、浏览、评论、焦点组、问卷 | **0** |
| OPD（他人的数据：竞品、行业报告、市场规模预测） | **0**（仅参考） |
| 已验证邮箱 | 1 / 个 |
| 已验证电话 | 10 / 个 |
| 用户投入的时间 | 1 / 分钟 |
| 真金白银（订金、预售、付费） | 1 / 元 |

**TRI 计量仪** —— 把试验结果映射成成功可能性：

| 数据 vs 假说预测 | 刻度 | 成功可能性 |
|---|---|---|
| 大大超过 | 非常有可能 | 90% |
| 达到或略微超过 | 有可能 | 70% |
| 略低于 | 不可能 | 30% |
| 远低于 | 非常不可能 | 10% |
| 模糊 / 受污染 / 难诠释 | 50/50 或丢弃 | 50% |

**硬性约束**：单次试验永远不够。至少 **3～5 次**，且次数与投资规模成正比。

---

## 安装

Claude Code 会从以下位置自动发现 skill：

- **全局**：`~/.claude/skills/<skill-name>/SKILL.md`
- **项目级**：`<project>/.claude/skills/<skill-name>/SKILL.md`

> ⚠️ 目录名必须保持为 **`right-it-check`**，与 `SKILL.md` 里的 `name:` 一致。

### 全局安装（推荐）

macOS / Linux：

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/Grimm57/the-right-it-skill.git ~/.claude/skills/right-it-check
```

Windows PowerShell：

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills" | Out-Null
git clone https://github.com/Grimm57/the-right-it-skill.git "$env:USERPROFILE\.claude\skills\right-it-check"
```

### 项目级安装

```bash
mkdir -p .claude/skills
git clone https://github.com/Grimm57/the-right-it-skill.git .claude/skills/right-it-check
```

### 手动安装

下载本仓库 ZIP，解压后把整个目录重命名为 `right-it-check`，放进上述任一 `skills/` 目录即可。无需安装依赖，只需要 Python 3.8+（仅命令行工具需要）。

---

## 怎么用

安装后，直接对 Claude Code 说出你的创意即可：

> 我想做一个「通勤巴士变课堂」的服务，帮 agent 用这个 skill 质检一下。

> 我打算开一家只做晚餐的社区烘焙工作室，值不值得做？

> 帮我验证这个 SaaS 创意：给独立咖啡店做自动排班。

> Use the right-it-check skill to pressure-test this idea: an AI meeting-notes tool for freelance consultants.

Skill 会在以下场景自动触发：你提出产品 / 服务 / 业务 / 内容创意，问「值不值得做」「市场会不会买账」「怎么验证」「怎么低成本试一下」，或要求撰写 XYZ 假说、设计预型试验。

典型用法是**一次对话跑完全流程**。信息不足时，skill 会把空白标成 `【待确认】` 并给出清单，而不是凭空编数字。

## 命令行工具

`scripts/rightit.py` 提供三个子命令，skill 会自动调用，你也可以手动跑：

```bash
cd ~/.claude/skills/right-it-check

# 1. 审计手上的证据，折算成切身利益点数
python scripts/rightit.py sitch --in examples/evidence.json

# 2. 给试验结果打分，并生成 TRI 计量仪可视化
python scripts/rightit.py tri --in examples/experiments.json --html tri.html

# 3. 按 DTD / HTD / $TD 给试验方案排序
python scripts/rightit.py plan --in examples/hypotheses.json
```

三个示例输入文件就在 [`examples/`](examples/) 下，开箱即跑。完整 JSON 格式见 [`references/analysis-tools.md`](references/analysis-tools.md#cli-输入-json-格式)。

<details>
<summary>示例输出（sitch）</summary>

```
==============================================================
切身利益卡尺 · 证据审计
==============================================================
创意：通勤巴士变课堂

【真正的 YODA】可以和市场失败律抗衡的部分
--------------------------------------------------------------
证据                          计分规则                            得分
已验证邮箱                    120 个 × 1 点                      120
已验证电话                    18 个 × 10 点                      180
参加 60 分钟宣讲会            30 人 × 60 分钟 × 1 点/分钟      1,800
预售订单                      12 笔 × ¥199 × 1 点/元          2,388
--------------------------------------------------------------
合计                                                       4,488 点
...
```
</details>

---

## 文件结构

```
the-right-it-skill/
├── SKILL.md                        主流程，agent 首先读这个
├── README.md
├── LICENSE
├── references/
│   ├── concepts.md                 市场失败律、正确的它、空想之地、四大怪、YODA/OPD、FLOP
│   ├── hypothesis-tools.md         MEH / XYZ / 缩进假说的写法与示例
│   ├── pretotype-tools.md          八种预型技术 + 选型决策树 + 合规边界
│   ├── analysis-tools.md           切身利益卡尺计分表 + TRI 判定细则 + JSON 格式
│   ├── tactics.md                  四条可塑性战术 + DTD/HTD/$TD
│   ├── materials-templates.md      各类预型物料模板
│   └── case-library.md             书中案例索引（按论证需求分组）
├── assets/
│   ├── report-template.md          质检报告模板
│   └── tri-gauge.html              TRI 计量仪可视化（自包含，可离线打开）
├── scripts/
│   └── rightit.py                  sitch / tri / plan 三个子命令
└── examples/
    ├── evidence.json               证据审计示例
    ├── experiments.json            试验判定示例
    └── hypotheses.json             试验规划示例
```

## 内置的合规红线

Skill 里写死了几条约束，避免 agent 给出有法律或伦理风险的方案：

- **医疗、健康、金融**等涉及人身或财产安全的品类**禁用假门预型** → 自动改用假面预型
- 使用假门**必须**配套坦白文案与补偿方案
- **潜入者预型一律用合规版本**（付费租用个体商户展示位），不采用原书中「假冒员工潜入卖场」的做法
- 预型物料首屏必须**明示价格**（避免 BusU 案例中「以为免费」污染数据的问题）

---

## 方法论出处与免责声明

本项目是 **非官方** 的社区作品，与 Alberto Savoia 本人及原书出版方**无任何隶属或授权关系**。

- 方法论与概念名称来自 Alberto Savoia 所著 *The Right It*（中译《做对产品》）。建议购买正版书籍系统阅读。
- 仓库**不包含**原书 PDF 或大段原文；`case-library.md` 是对公开案例的摘要与评论，仅用于教学与论证参考。
- 书中所有案例都是轶事证据，按作者本人的警告，应作为 **OPD（他人的数据）** 看待，**不能**用来判断你自己的创意是否可行。
- 本工具输出不构成投资、法律或商业决策建议。

## 参与贡献

欢迎提交 Issue 和 PR：

- 修正方法论表述或中文翻译
- 补充新的预型物料模板与案例（请注明来源）
- 改进 `rightit.py` 的输入校验与输出
- 增加英文文档与更多语言的本地化

提交前请确保示例仍可运行：

```bash
python scripts/rightit.py sitch --in examples/evidence.json
python scripts/rightit.py tri --in examples/experiments.json
python scripts/rightit.py plan --in examples/hypotheses.json
```

## License

[MIT](LICENSE) © 2026 Grimm57

---

# English

**right-it-check** is a [Claude Code](https://claude.com/claude-code) skill that pressure-tests a product idea before you build it, using the methodology from Alberto Savoia's *The Right It*.

It turns a vague idea into a falsifiable **XYZ hypothesis** (“at least X% of Y will do Z”), audits your existing evidence with the **Skin-in-the-Game Lens** (opinions and OPD score zero; verified emails, phone numbers, time, and money score points), designs cheap **pretotype** experiments ranked by **DTD / HTD / $TD**, generates ready-to-ship materials, and renders a verdict with the **TRI meter** — *go for it / adjust it / drop it*.

Install globally:

```bash
git clone https://github.com/Grimm57/the-right-it-skill.git ~/.claude/skills/right-it-check
```

Then ask Claude Code:

> Use the right-it-check skill to validate this idea: an AI meeting-notes tool for freelance consultants.

CLI (Python 3.8+, no dependencies):

```bash
python scripts/rightit.py sitch --in examples/evidence.json
python scripts/rightit.py tri    --in examples/experiments.json --html tri.html
python scripts/rightit.py plan   --in examples/hypotheses.json
```

This is an unofficial community project, not affiliated with or endorsed by Alberto Savoia or the publisher. The book is not included. Licensed under MIT.
