#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rightit.py — 《做对产品》(The Right It) 质检工具集

三个子命令：
  sitch   切身利益卡尺：把一堆"证据"折算成切身利益点数
  tri     TRI 计量仪：把试验结果映射到 5 级刻度并判定
  plan    按 DTD / HTD / $TD 给试验方案排序

用法：
  python rightit.py sitch --in evidence.json
  python rightit.py tri   --in experiments.json [--html tri.html]
  python rightit.py plan  --in hypotheses.json

JSON 格式见 SKILL.md 或 references/analysis-tools.md 末尾。
"""

import argparse
import json
import sys
from pathlib import Path

# Windows 控制台默认 GBK，输出 ¥ 和中文标点会报 UnicodeEncodeError。
# 强制 stdout/stderr 走 UTF-8；Python 3.7+ 支持 reconfigure。
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

# 切身利益卡尺点数（《做对产品》第 6 章）
SITCH_POINTS = {
    "email": 1,       # 已验证邮箱，每个 1 点
    "phone": 10,      # 已验证电话，每个 10 点
    "time": 1,        # 用户投入时间，每分钟 1 点
    "money": 1,       # 真金白银，每元 1 点
}

# 0 点证据
ZERO_POINT_TYPES = {
    "opinion": "意见（不管是谁的）",
    "opd": "OPD — 他人的数据",
    "vanity": "虚荣指标（浏览/点赞/转发/评论/投票）",
    "focus_group": "焦点组反馈",
    "survey": "问卷/投票结果",
}

# TRI 计量仪 5 级刻度
TRI_SCALE = [
    (10, "非常不可能"),
    (30, "不可能"),
    (50, "50/50"),
    (70, "有可能"),
    (90, "非常有可能"),
]

# 投资级别 → 建议的最少试验次数
MIN_EXPERIMENTS = {"low": 3, "medium": 5, "high": 8}


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def load_json(path):
    p = Path(path)
    if not p.exists():
        die(f"找不到文件：{path}")
    try:
        with p.open(encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        die(f"JSON 解析失败（{path}）：{e}")


def die(msg, code=1):
    print(f"错误：{msg}", file=sys.stderr)
    sys.exit(code)


def fmt_money(v):
    """金额格式化，去掉多余的小数位。"""
    if v == int(v):
        return f"{int(v):,}"
    return f"{v:,.2f}"


def bar(score):
    """把 10-90 的刻度画成一行示意。"""
    idx = min(range(len(TRI_SCALE)), key=lambda i: abs(TRI_SCALE[i][0] - score))
    cells = []
    for i, (val, _) in enumerate(TRI_SCALE):
        cells.append("■" if i == idx else "·")
    return " ".join(cells)


# ---------------------------------------------------------------------------
# 子命令 1：切身利益卡尺
# ---------------------------------------------------------------------------

def cmd_sitch(args):
    data = load_json(args.input)
    items = data.get("evidence", [])
    if not items:
        die("evidence.json 里没有 evidence 数组")

    yoda_rows = []
    zero_rows = []
    total = 0.0

    for it in items:
        t = (it.get("type") or "").strip().lower()
        label = it.get("label") or t
        count = it.get("count", 0) or 0

        if t in SITCH_POINTS:
            unit = SITCH_POINTS[t]
            if t == "time":
                # 每人投入的分钟数
                minutes = it.get("unit_minutes", 0) or 0
                score = count * minutes * unit
                rule = f"{count} 人 × {minutes} 分钟 × {unit} 点/分钟"
            elif t == "money":
                amount = it.get("amount_each", 0) or 0
                score = count * amount * unit
                rule = f"{count} 笔 × ¥{fmt_money(amount)} × {unit} 点/元"
            else:
                score = count * unit
                rule = f"{count} 个 × {unit} 点"
            total += score
            yoda_rows.append((label, count, rule, score))

        elif t in ZERO_POINT_TYPES:
            reason = ZERO_POINT_TYPES[t]
            if t == "opd":
                reason += "。可参考，不能依赖，不能替代你自己的数据"
            zero_rows.append((label, count, reason))

        else:
            zero_rows.append((label, count, f"未知类型 '{t}'，按 0 点处理"))

    # ---- 输出 ----
    out = []
    out.append("=" * 62)
    out.append("切身利益卡尺 · 证据审计")
    out.append("=" * 62)
    if data.get("creative"):
        out.append(f"创意：{data['creative']}")
    out.append("")

    out.append("【真正的 YODA】可以和市场失败律抗衡的部分")
    out.append("-" * 62)
    if yoda_rows:
        out.append(f"{'证据':<28}{'计分规则':<26}{'得分':>8}")
        for label, _, rule, score in yoda_rows:
            disp = label if len(label) <= 26 else label[:25] + "…"
            out.append(f"{disp:<28}{rule:<26}{score:>8,.0f}")
        out.append("-" * 62)
        out.append(f"{'合计':<54}{total:>8,.0f} 点")
    else:
        out.append("（无）")
    out.append("")

    out.append("【0 点证据】不能作为决策依据")
    out.append("-" * 62)
    if zero_rows:
        for label, count, reason in zero_rows:
            out.append(f"· {label}（{count}）")
            out.append(f"    → {reason}")
    else:
        out.append("（无）")
    out.append("")

    # ---- 结论 ----
    out.append("=" * 62)
    n_zero = len(zero_rows)
    if total == 0:
        out.append("结论：你手上没有任何真正的 YODA。")
        out.append("      所有证据都是 0 点的意见 / OPD / 虚荣指标。")
        out.append("      → 目前无法对创意价值做任何判断，先跑预型试验。")
    else:
        out.append(f"结论：真正能与市场失败律抗衡的证据是 {total:,.0f} 点。")
        if n_zero:
            out.append(f"      另有 {n_zero} 类 0 点证据——它们说明「大家觉得不错」，")
            out.append("      但没有一个人在承担风险。")
        if total < 100:
            out.append("      点数偏低（<100）。即使全部为真，证据强度仍不足以支撑重大投入。")
        out.append("      → 需要预型试验补齐证据。")
    out.append("=" * 62)

    print("\n".join(out))
    if args.json:
        Path(args.json).write_text(
            json.dumps({"total_points": total,
                        "yoda": [{"label": l, "count": c, "rule": r, "points": s}
                                 for l, c, r, s in yoda_rows],
                        "zero_point": [{"label": l, "count": c, "reason": r}
                                       for l, c, r in zero_rows]},
                       ensure_ascii=False, indent=2),
            encoding="utf-8")
        print(f"\n（已写出 JSON：{args.json}）")


# ---------------------------------------------------------------------------
# 子命令 2：TRI 计量仪
# ---------------------------------------------------------------------------

def map_to_scale(predicted, actual, confounded=False):
    """把试验结果映射到 5 级刻度。返回 (score, label, reason)。"""
    if confounded:
        return 50, "50/50", "数据受混淆因素影响，尚无论断；考虑丢弃或重测"

    if predicted <= 0:
        return 50, "50/50", "假说预测值为 0，无法比较"

    ratio = actual / predicted

    if ratio >= 1.5:
        return 90, "非常有可能", "数据大大超过假说预测"
    if ratio >= 1.0:
        return 70, "有可能", "数据达到或略微超过假说预测"
    if ratio >= 0.5:
        return 30, "不可能", "数据略低于假说预测"
    return 10, "非常不可能", "数据远低于假说预测"


def cmd_tri(args):
    data = load_json(args.input)
    experiments = data.get("experiments", [])
    if not experiments:
        die("experiments.json 里没有 experiments 数组")

    rows = []
    for e in experiments:
        pred = float(e.get("predicted_pct", 0) or 0)
        act = float(e.get("actual_pct", 0) or 0)
        conf = bool(e.get("confounded", False))
        score, label, reason = map_to_scale(pred, act, conf)
        rows.append({
            "id": e.get("id", len(rows) + 1),
            "name": e.get("name", f"试验{len(rows)+1}"),
            "hypothesis": e.get("hypothesis", ""),
            "predicted": pred,
            "actual": act,
            "n": e.get("n", 0),
            "score": score,
            "label": label,
            "reason": reason,
            "note": e.get("note", ""),
            "confounded": conf,
        })

    # ---- 输出 ----
    out = []
    out.append("=" * 74)
    out.append("TRI 计量仪 · 试验结果判定")
    out.append("=" * 74)
    if data.get("creative"):
        out.append(f"创意：{data['creative']}")
    out.append("")

    out.append(f"{'#':<3}{'试验':<16}{'假说预测':>10}{'实际结果':>10}{'样本':>8}  {'刻度':<10}{'判定':<8}")
    out.append("-" * 74)
    for r in rows:
        name = r["name"] if len(r["name"]) <= 14 else r["name"][:13] + "…"
        out.append(f"{r['id']:<3}{name:<16}"
                   f"{r['predicted']:>9.0f}%{r['actual']:>9.0f}%{r['n']:>8}  "
                   f"{r['label']:<10}{r['score']:>5}%")
    out.append("")

    # 刻度图
    out.append("刻度分布：")
    for r in rows:
        out.append(f"  试验{r['id']:<3}{bar(r['score'])}  {r['score']}%  {r['reason']}")
    out.append("")
    out.append("  刻度轴： 10% 非常不可能 ─ 30% 不可能 ─ 50% 50/50 ─ 70% 有可能 ─ 90% 非常有可能")
    out.append("")

    # ---- 汇总判定 ----
    k = len(rows)
    positives = sum(1 for r in rows if r["score"] >= 70)
    negatives = sum(1 for r in rows if r["score"] <= 30)
    neutral = k - positives - negatives
    avg = sum(r["score"] for r in rows) / k

    level = (data.get("investment_level") or "medium").lower()
    need = data.get("min_experiments") or MIN_EXPERIMENTS.get(level, 5)

    out.append("=" * 74)
    out.append("综合判定")
    out.append("-" * 74)
    out.append(f"试验次数         {k} 次（建议至少 {need} 次，投资级别：{level}）"
               f"  {'✅' if k >= need else '❌ 不足'}")
    out.append(f"正面 / 负面      {positives} 正 / {negatives} 负"
               + (f" / {neutral} 存疑" if neutral else ""))
    out.append(f"平均成功可能性   {avg:.0f}%")

    # 一致性检查：正面结果是否集中
    if positives and negatives:
        out.append("")
        out.append("⚠️  结果不一致：同时存在明确正面和明确负面的试验。")
        out.append("    这通常意味着创意只有部分版本成立——按版本分别判定，")
        out.append("    并考虑放弃被证伪的那个版本（参照 BusU 案例：3 000 元长课程被证伪）。")

    if k < need:
        out.append("")
        out.append(f"⚠️  试验次数不足：单次或少数几次试验永远不够。")
        out.append(f"    需要再跑 {need - k} 次，才能对抗市场失败律。")
        out.append("    试验次数应与投资规模成正比——要辞职或押上公司资金的话，还要更多。")

    out.append("")
    out.append("─" * 74)
    out.append("提醒：底部始终有一个指向「非常不可能」的黑色大箭头——那是市场失败律。")
    out.append("      只有多次一致的正面结果才能抵消它。")
    out.append("      只有精心设计和亲自执行的试验产生的 YODA 才有资格标在上面。")
    out.append("=" * 74)

    print("\n".join(out))

    if args.html:
        write_html(args.html, data.get("creative", "创意"), rows,
                   positives, negatives, k, need, avg)
        print(f"\n（已生成可视化：{args.html}）")

    if args.json:
        Path(args.json).write_text(
            json.dumps({"rows": rows, "positives": positives,
                        "negatives": negatives, "average": round(avg, 1),
                        "experiments": k, "recommended_min": need},
                       ensure_ascii=False, indent=2),
            encoding="utf-8")
        print(f"（已写出 JSON：{args.json}）")


def write_html(path, creative, rows, positives, negatives, k, need, avg):
    """生成自包含的 TRI 计量仪可视化页面。"""
    lanes = []
    for r in rows:
        idx = min(range(len(TRI_SCALE)), key=lambda i: abs(TRI_SCALE[i][0] - r["score"]))
        lanes.append({"name": r["name"], "idx": idx, "score": r["score"],
                      "predicted": r["predicted"], "actual": r["actual"],
                      "n": r["n"], "reason": r["reason"], "note": r["note"]})

    payload = json.dumps({"creative": creative, "lanes": lanes,
                          "positives": positives, "negatives": negatives,
                          "k": k, "need": need, "avg": round(avg, 1)},
                         ensure_ascii=False)
    # 防止数据中出现的 "</script>" 或 "<!--" 提前截断脚本块
    payload = payload.replace("</", "<\\/").replace("<!--", "<\\!--")

    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TRI 计量仪 — __CREATIVE__</title>
<style>
  :root{
    --bg:#0f1115; --card:#171a21; --fg:#e8eaed; --muted:#9aa3b2;
    --line:#252a34; --ok:#3ddc97; --warn:#ffc857; --bad:#ff6b6b;
    --c10:#c0392b; --c30:#e67e22; --c50:#8e8e93; --c70:#4f8cff; --c90:#3ddc97;
  }
  @media (prefers-color-scheme: light){
    :root{--bg:#fbfbfd;--card:#fff;--fg:#14171c;--muted:#5f6774;--line:#e6e9ef;}
  }
  *{box-sizing:border-box;margin:0;padding:0}
  body{
    background:var(--bg);color:var(--fg);padding:32px 20px;
    font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
  }
  .wrap{max-width:960px;margin:0 auto}
  h1{font-size:24px;letter-spacing:-.02em;margin-bottom:6px}
  .sub{color:var(--muted);font-size:14px;margin-bottom:28px}
  .card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:26px;margin-bottom:20px}
  .axis{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin-bottom:18px}
  .axis div{
    text-align:center;font-size:12px;color:var(--muted);padding:8px 4px;
    border-bottom:3px solid var(--line);
  }
  .axis div b{display:block;font-size:15px;color:var(--fg);margin-bottom:2px}
  .lane{
    display:grid;grid-template-columns:repeat(5,1fr);gap:8px;
    align-items:center;padding:9px 0;border-bottom:1px dashed var(--line);
  }
  .lane:last-child{border-bottom:0}
  .dot{
    width:100%;height:16px;border-radius:4px;background:transparent;
    display:flex;align-items:center;justify-content:center;
  }
  .dot.on{position:relative}
  .dot.on::after{
    content:"";width:0;height:0;
    border-top:8px solid transparent;border-bottom:8px solid transparent;
    border-right:13px solid currentColor;
    filter:drop-shadow(0 0 4px currentColor);
  }
  .lname{font-size:13px;color:var(--muted);margin-top:2px}
  .floor{
    margin-top:20px;padding:14px 18px;border-radius:10px;
    background:rgba(192,57,43,.12);border:1px solid rgba(192,57,43,.4);
    color:var(--c10);font-size:13px;
  }
  @media (prefers-color-scheme: dark){ .floor{color:#ff8a7a} }
  table{width:100%;border-collapse:collapse;font-size:13px;margin-top:14px}
  th,td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line)}
  th{color:var(--muted);font-weight:500;font-size:12px}
  td.num{text-align:right;font-variant-numeric:tabular-nums}
  .summary{display:flex;gap:28px;flex-wrap:wrap;margin-top:4px}
  .stat b{display:block;font-size:26px;letter-spacing:-.02em}
  .stat span{color:var(--muted);font-size:12px}
  .pill{display:inline-block;padding:3px 10px;border-radius:20px;font-size:12px;margin-top:12px}
  .pill.ok{background:rgba(61,220,151,.15);color:var(--ok)}
  .pill.warn{background:rgba(255,200,87,.15);color:var(--warn)}
  .pill.bad{background:rgba(255,107,107,.15);color:var(--bad)}
</style>
</head>
<body>
<div class="wrap">
  <h1 id="title"></h1>
  <p class="sub">TRI 计量仪（"正确的它"计量仪）· 由《做对产品》方法论生成</p>

  <div class="card">
    <div class="summary" id="summary"></div>
    <div id="pill"></div>
  </div>

  <div class="card">
    <div class="axis">
      <div><b>10%</b>非常不可能</div>
      <div><b>30%</b>不可能</div>
      <div><b>50%</b>50/50</div>
      <div><b>70%</b>有可能</div>
      <div><b>90%</b>非常有可能</div>
    </div>
    <div id="lanes"></div>
    <div class="floor">
      ▲ 市场失败律：大多数新产品都将在市场上失败，即使所有环节执行到位也避免不了。
      只有多次一致的正面结果才能抵消它。
    </div>
  </div>

  <div class="card">
    <table>
      <thead><tr>
        <th>试验</th><th>假说预测</th><th>实际结果</th><th>样本</th>
        <th>刻度</th><th>判定依据</th>
      </tr></thead>
      <tbody id="tbody"></tbody>
    </table>
  </div>
</div>

<script>
const DATA = __PAYLOAD__;
const COLORS = ['--c10','--c30','--c50','--c70','--c90'];
const LABELS = ['非常不可能','不可能','50/50','有可能','非常有可能'];
const SCORES = [10,30,50,70,90];

document.getElementById('title').textContent = 'TRI 计量仪 — ' + DATA.creative;

const s = document.getElementById('summary');
s.innerHTML = `
  <div class="stat"><b>${DATA.k}</b><span>已运行试验次数</span></div>
  <div class="stat"><b>${DATA.avg}%</b><span>平均成功可能性</span></div>
  <div class="stat"><b>${DATA.positives} / ${DATA.negatives}</b><span>正面 / 负面</span></div>
  <div class="stat"><b>${DATA.need}</b><span>建议最少试验次数</span></div>
`;

const pill = document.getElementById('pill');
let cls = 'ok', msg = '试验次数达标，结果方向明确。';
if (DATA.k < DATA.need) { cls='warn'; msg=`试验次数不足（${DATA.k}/${DATA.need}）。单次或少数几次试验永远不够——需要继续测试才能对抗市场失败律。`; }
if (DATA.positives && DATA.negatives) { cls='warn'; msg += ' 同时存在明确正面与明确负面结果：可能只有部分版本成立，建议按版本分别判定。'; }
if (!DATA.positives && DATA.negatives) { cls='bad'; msg='目前没有正面结果。多数情况下，正确做法是回到绘图板调整创意，而不是加大投入。'; }
pill.innerHTML = `<span class="pill ${cls}">${msg}</span>`;

const lanes = document.getElementById('lanes');
const tbody = document.getElementById('tbody');

DATA.lanes.forEach((l, i) => {
  const row = document.createElement('div');
  row.className = 'lane';
  for (let c = 0; c < 5; c++) {
    const d = document.createElement('div');
    d.className = 'dot' + (c === l.idx ? ' on' : '');
    if (c === l.idx) d.style.color = `var(${COLORS[c]})`;
    row.appendChild(d);
  }
  lanes.appendChild(row);

  const name = document.createElement('div');
  name.className = 'lname';
  name.textContent = `试验 #${i+1} · ${l.name}`;
  lanes.appendChild(name);

  const tr = document.createElement('tr');
  tr.innerHTML = `
    <td>#${i+1} ${l.name}${l.note ? `<br><span style="color:var(--muted);font-size:12px">${l.note}</span>` : ''}</td>
    <td class="num">≥${l.predicted}%</td>
    <td class="num">${l.actual}%</td>
    <td class="num">${l.n}</td>
    <td style="color:var(${COLORS[l.idx]});font-weight:600">${l.score}% ${LABELS[l.idx]}</td>
    <td style="color:var(--muted)">${l.reason}</td>
  `;
  tbody.appendChild(tr);
});
</script>
</body>
</html>
"""
    html = html.replace("__CREATIVE__", creative).replace("__PAYLOAD__", payload)
    Path(path).write_text(html, encoding="utf-8")


# ---------------------------------------------------------------------------
# 子命令 3：试验规划
# ---------------------------------------------------------------------------

def cmd_plan(args):
    data = load_json(args.input)
    hyps = data.get("hypotheses", [])
    if not hyps:
        die("hypotheses.json 里没有 hypotheses 数组")

    # 归一化到 0-1 区间后加权，分数越低越优先
    def norm(vals):
        lo, hi = min(vals), max(vals)
        if hi == lo:
            return [0.5] * len(vals)
        return [(v - lo) / (hi - lo) for v in vals]

    dtds = [float(h.get("dtd", 0) or 0) for h in hyps]
    htds = [float(h.get("htd", 0) or 0) for h in hyps]
    costs = [float(h.get("cost", 0) or 0) for h in hyps]

    n_dtd, n_htd, n_cost = norm(dtds), norm(htds), norm(costs)

    scored = []
    for i, h in enumerate(hyps):
        # HTD 权重最高：先测胜过后测
        total = n_htd[i] * 0.5 + n_cost[i] * 0.3 + n_dtd[i] * 0.2
        scored.append({
            "h": h,
            "dtd": dtds[i], "htd": htds[i], "cost": costs[i],
            "priority": total,
            "sitch": float(h.get("sitch_points", 0) or 0),
        })
    scored.sort(key=lambda x: x["priority"])

    out = []
    out.append("=" * 78)
    out.append("试验规划 · 按 DTD / HTD / $TD 排序")
    out.append("=" * 78)
    if data.get("creative"):
        out.append(f"创意：{data['creative']}")
    out.append("")
    out.append("排序原则：先测胜过后测（HTD 权重最高）→ 便宜更好（$TD）→ 本地优先（DTD）")
    out.append("")

    out.append(f"{'序':<4}{'假说':<8}{'DTD':>8}{'HTD(h)':>10}{'$TD':>10}{'切身利益':>10}  {'建议':<12}")
    out.append("-" * 78)
    for rank, s in enumerate(scored, 1):
        h = s["h"]
        hid = h.get("id", f"xyz{rank}")
        if rank == 1:
            advice = "先跑这个"
        elif s["htd"] > 48 or s["cost"] > 500:
            advice = "投资较大，最后跑"
        else:
            advice = "等前一个结果"
        out.append(f"{rank:<4}{hid:<8}{s['dtd']:>8.0f}{s['htd']:>10.0f}"
                   f"{s['cost']:>10,.0f}{s['sitch']:>10.0f}  {advice:<12}")
    out.append("")

    out.append("假说内容：")
    for rank, s in enumerate(scored, 1):
        h = s["h"]
        out.append(f"  {rank}. [{h.get('id', f'xyz{rank}')}] {h.get('text', '(无描述)')}")
    out.append("")

    # ---- 达标检查 ----
    out.append("=" * 78)
    out.append("指标达标检查")
    out.append("-" * 78)
    for rank, s in enumerate(scored, 1):
        h = s.get("h", {})
        hid = h.get("id", f"xyz{rank}")
        flags = []
        flags.append(("HTD", s["htd"] <= 48, f"{s['htd']:.0f}h（目标 ≤48h）"))
        flags.append(("$TD", s["cost"] <= 500, f"¥{s['cost']:,.0f}（目标 ≈ 一次团队午餐）"))
        out.append(f"{hid}：")
        for name, ok, detail in flags:
            status = "达标" if ok else "超标"
            out.append(f"   {'✅' if ok else '⚠️ '} {name} {status} — {detail}")
    out.append("")

    # ---- 连锁逻辑 ----
    if len(scored) > 1:
        first = scored[0]["h"].get("id", "xyz1")
        second = scored[1]["h"].get("id", "xyz2")
        out.append("连锁决策逻辑：")
        out.append(f"  · 若 {first} 通过 → 投入测试 {second}")
        out.append(f"  · 若 {first} 不通过 → 回到阶段 1 调整假说，")
        out.append(f"    不要直接跳到投资更大的试验（10 次小微调好过一次痛苦的关键转型）")
        out.append("")

    # ---- 降级挑战 ----
    worst = max(scored, key=lambda x: x["cost"])
    if worst["cost"] > 0:
        out.append("降级挑战（战术 3：琢磨便宜、更便宜、最便宜）：")
        out.append(f"  当前最贵的一项：{worst['h'].get('id','')} ¥{worst['cost']:,.0f}")
        out.append(f"  → 能否降到 1/10？  ¥{worst['cost']/10:,.0f}")
        out.append(f"  → 能否降到 1/100？ ¥{worst['cost']/100:,.0f}")
        out.append("  问自己：这是我们能做到的最好的吗？继续尝试做到更好。")
    out.append("=" * 78)

    print("\n".join(out))


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        prog="rightit",
        description="《做对产品》创意质检工具集",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="JSON 输入格式见 references/analysis-tools.md 末尾。",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("sitch", help="切身利益卡尺：折算证据点数")
    p1.add_argument("--in", dest="input", required=True, help="evidence.json")
    p1.add_argument("--json", help="把结果另存为 JSON")
    p1.set_defaults(func=cmd_sitch)

    p2 = sub.add_parser("tri", help="TRI 计量仪：判定试验结果")
    p2.add_argument("--in", dest="input", required=True, help="experiments.json")
    p2.add_argument("--html", help="生成可视化 HTML")
    p2.add_argument("--json", help="把结果另存为 JSON")
    p2.set_defaults(func=cmd_tri)

    p3 = sub.add_parser("plan", help="按 DTD/HTD/$TD 排序试验方案")
    p3.add_argument("--in", dest="input", required=True, help="hypotheses.json")
    p3.set_defaults(func=cmd_plan)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
