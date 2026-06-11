# mentorly-outreach

Mentorly 早期获客触达工具包（v2：seed user + reply yes）

**主仓库：** [SmartAIMentor/Mentoraixs](https://github.com/SmartAIMentor/Mentoraixs)

## 目录

| 路径 | 说明 |
|------|------|
| `batch_email_tiktok.py` | TikTok 冷邮件 → Instantly CSV |
| `batch_outreach.py` | IG DM（TikHub + v2 模板） |
| `template_render.py` | 加载 `templates/*_v2.txt` |
| `creators_tiktok.csv` | 300 人邮件名单 |
| `creators.csv` | IG DM 名单（与邮件不重合） |
| `templates/` | v1 + v2 话术 |
| `crm-触达追踪_飞书导入.csv` | batch1 250 人 CRM 模板 |
| `运营事项_更新.csv` | 三阶段运营任务 |
| `docs/` | P0 测试、onboarding、内容交付物 |

## 快速开始

```bash
cp .env.example .env   # 可选：TIKHUB_API_KEY
./run.sh email --limit 250
python generate_crm_batch1.py
```

## 话术（v2）

| 渠道 | 模板 | CTA |
|------|------|-----|
| 冷邮件 | `templates/EMAIL_en_v2.txt` | 回复 **yes** |
| DM | `templates/DM_en_v2.txt` | 回复 **yes** |
| Reddit | `templates/REDDIT_en_v2.txt` | yes |

Tally (`https://tally.so/r/Bz05RK`) 仅备用留资。

## CTA 切换

1. **现在**：reply yes  
2. **测通 Leroy 后**：产品注册链接 → 见 `docs/leroy-p0-test-checklist.md`  
3. **有留存后**：付费/订阅  

Seed onboarding：`docs/seed-onboarding-sop.md`

## Instantly

1. 导入 `output/tiktok_email_ready_*.csv`
2. Subject=`{{email_subject}}`，Body=`{{email_body}}`
3. Daily Limit **30–50/天**

## CRM 状态

`待触达` → `已发` → `已回` → `已注册` → `已激活`（见 `crm-字段说明.md`）

详细说明见 [`README-outreach.md`](README-outreach.md)（与 Mentoraixs `scripts/outreach/README.md` 同步）。
