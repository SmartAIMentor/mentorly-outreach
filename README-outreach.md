# 达人触达 · 一键执行

仓库：[SmartAIMentor/mentorly-outreach](https://github.com/SmartAIMentor/mentorly-outreach)

## 当前话术（v2）

| 渠道 | 模板 | CTA |
|------|------|-----|
| 冷邮件 | `templates/EMAIL_en_v2.txt` | 回复 **yes**（无 Tally 链接） |
| IG/TikTok DM | `templates/DM_en_v2.txt` | 回复 **yes** |
| Reddit | `templates/REDDIT_en_v2.txt` | 评论/DM yes |

**Tally** (`https://tally.so/r/Bz05RK`) 仅作备用留资，不再是邮件主 CTA。

## CTA 切换规则

| 阶段 | CTA | 条件 |
|------|-----|------|
| 现在 | reply yes | 默认 |
| 下一步 | 产品注册链接 | [Leroy P0 测试清单](../../docs/mvp/leroy-p0-test-checklist.md) 全部通过 |
| 之后 | 付费/订阅 | 有稳定激活数据 |

Seed 用户回复 yes 后流程：[`docs/seed-onboarding-sop.md`](../../docs/seed-onboarding-sop.md)

## 名单不重合

- **邮件 batch1**：Instantly 先发 250 人（`creators_tiktok.csv` 前 250）
- **IG DM**：只用 `creators.csv`，**不在** batch1 邮件名单
- 邮件未回 → 可 DM 补触达

## 快速命令

```bash
cd scripts/outreach
cp .env.example .env   # TIKHUB_API_KEY 可选

./run.sh import        # xlsx → creators_tiktok.csv + 运营事项 CSV
./run.sh email --limit 250   # TikTok 冷邮件 → Instantly 导入
./run.sh               # IG DM 文案（creators.csv）
python export_ops_xlsx.py    # 运营事项 CSV → xlsx
```

## Instantly 导入

1. 上传 `output/tiktok_email_ready_*.csv`
2. 映射：`email` → Email，`name` → First Name，`email_subject` / `email_body` → Custom Variable
3. Sequences：Subject=`{{email_subject}}`，Body=`{{email_body}}`
4. Daily Limit：**30–50/天**（Gmail 预热），不要第一天 250

## CRM

飞书导入：[`docs/crm-触达追踪_飞书导入.csv`](../../docs/crm-触达追踪_飞书导入.csv)  
字段说明：[`docs/crm-字段说明.md`](../../docs/crm-字段说明.md)

## 运营任务表

最新任务（对齐 Leroy + JD）：[`docs/运营事项_更新.csv`](../../docs/运营事项_更新.csv)
