# CRM 状态字段说明

飞书多维表格导入模板：[`crm-触达追踪_飞书导入.csv`](crm-触达追踪_飞书导入.csv)

## 状态流转

```
待触达 → 已发 → 已回 → 已注册 → 已激活
                    ↘ 流失
```

| 状态 | 含义 | 谁更新 |
|------|------|--------|
| 待触达 | 在名单里，还没发 | 导入时默认 |
| 已发 | 邮件/DM 已发出 | Bonnie |
| 已回 | 回复 yes 或任意有效回复 | Bonnie |
| 已注册 | 已创建产品账号 | Bonnie / 晓宇 |
| 已激活 | 至少完成 1 次 Chat | 晓宇 |
| 流失 | 7 天无回复或未注册 | Bonnie |

## 字段说明

| 字段 | 说明 |
|------|------|
| channel | `email` 或 `dm`，避免同人双通道 |
| email_batch | `batch1` / `batch2`，对应 Instantly 批次 |
| dm_sent | `yes` / `no` |
| reply_at | 首次回复日期 |
| registered_at | 注册日期 |
| activated_at | 首次 Chat 日期 |

## 名单不重合规则

- **邮件 batch1**：`creators_tiktok.csv` 前 250 人
- **IG DM**：只用 `creators.csv` 中 **不在** 邮件 batch1 的 IG 账号
- 邮件未回者 → 可进入 DM 补触达，CRM 里 `channel` 可记 `email+dm`
