# Mentorly Outreach & Operations

Mentorly 早期获客自动化与运营工具包。

## 仓库说明

本仓库包含 Mentorly 早期寻找 Beta 测试用户的触达脚本、模板和运营任务状态。

### 目录结构

- `batch_outreach.py`: Instagram 达人 DM/邮件自动化生成脚本 (基于 TikHub)。
- `batch_email_tiktok.py`: TikTok 达人冷邮件自动化生成脚本。
- `import_xlsx.py`: 从 `运营事项.xlsx` 导入达人名单和任务。
- `run.sh`: 一键执行脚本。
- `creators_tiktok.csv`: 导出的 TikTok 达人名单 (含邮箱)。
- `creators.csv`: Instagram 达人名单。
- `templates/`: DM 和邮件的文案模板。
- `*.md` / `*.csv`: 运营任务、飞书导入表和工具选型报告。

## 当前进度与状态

**整体目标**: 寻找 50 个 Beta 共建者，验证产品 PMF。

**已完成**:
1. 获客策略拆解为具体的飞书任务表 (`飞书任务表_Mentorly早期获客.csv`)。
2. 自动化生成个性化 DM 和邮件文案的脚本开发完毕。
3. 留资表单 (Tally) 已建好并集成到文案中。
4. 300 名 TikTok 达人邮箱名单已准备就绪，并生成了对应的冷邮件文案。

**卡点 (Blockers)**:
1. **文案审阅**: 需要人工审阅生成的 DM 和邮件措辞是否合适。如果合适，可以直接开始发送。
2. **Instantly 限制**: Instantly 免费版/试用版一次只能导入/发送 250 个 lead。目前有 300 个 TikTok 达人，需要**升级 Instantly 会员**才能完全自动化批量发送，或者先分批发送。

## 下一步行动

1. **审阅文案**: 检查 `templates/` 目录下的模板，或运行脚本查看生成的示例。
2. **升级/分批发送**: 决定是升级 Instantly 会员，还是将 300 人名单拆分后手动导入发送。
3. **开始 IG DM**: 每天手动复制生成的文案发送 20 条 IG DM。

## 运行脚本

```bash
# 复制环境变量模板并填入 TIKHUB_API_KEY 和 MENTORLY_BETA_FORM_URL
cp .env.example .env

# 生成 TikTok 邮件文案
./run.sh email

# 生成 IG DM 文案
./run.sh
```