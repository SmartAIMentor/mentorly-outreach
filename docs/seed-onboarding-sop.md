# Seed 用户 Onboarding SOP

> 对应任务 **P0-2**。达人回复邮件/DM **"yes"** 后的标准流程。

## 触发条件

- 冷邮件（Instantly）或 IG DM 收到回复 **yes** / **Yes** / **I'm interested**
- 记录到飞书 CRM，状态改为 **已回**

## 24 小时内动作

| 步骤 | 谁做 | 做什么 | 模板 |
|------|------|--------|------|
| 1 | Bonnie | 回复确认邮件/DM | 见下方「确认回复」 |
| 2 | Bonnie | 飞书 CRM 状态 → **已回** | — |
| 3 | 测通前 | 拉 Discord/微信群，说明 seed 身份 | 见下方「拉群话术」 |
| 4 | 测通后 | 发产品注册链接 + 说明免费 1 个月如何兑现 | 见下方「注册邀请」 |

## 确认回复（英文，复制即用）

```
Thanks for replying! You're on the seed list.

Next step: we'll add you to a small tester group and send access details within 48h.

Quick ask: what's your main platform (TikTok / IG / YouTube) and handle?

— The team
```

## 拉群话术（测通前）

```
Hey — adding you to our small seed tester group here.

We're still polishing the product; you'll get early access before public launch.

In return we'd love honest feedback on: (1) is the chat useful? (2) what's missing?

You'll get a free month ($60 value) when we go live — we'll confirm that in writing before you spend time.
```

## 注册邀请（Leroy 测通后）

```
Your early access is ready:

[产品注册链接]

1. Sign up with the same email you replied from
2. Try Chat once — ask anything about content or brand deals
3. Reply here with 1 thing you'd change

Your free month at launch is reserved for seed testers who complete step 2.
```

## 免费 1 个月兑现规则

| 条件 | 动作 |
|------|------|
| 已注册 + 至少 1 次 Chat | Bonnie 在 CRM 标 **已激活** |
| 产品正式上线 | 后台手动 grant 1 个月积分 / 或 Stripe 优惠码（晓宇配置） |
| 未注册 7 天 | 发 1 封 reminder，仍无回复 → 标 **流失** |

## CRM 状态流转

```
待触达 → 已发 → 已回 → 已注册 → 已激活
                    ↘ 流失
```

## 分工

| 角色 | 职责 |
|------|------|
| Bonnie | 回复 yes、拉群、跟进注册 |
| 晓宇 | 开试用权限、grant 积分、修 bug |
| 清酒 | 收集反馈写入 FAQ |
