# Leroy 分支 P0 联调测试清单

> 对应任务 **P0-1**。在 [Leroy 分支](https://github.com/SmartAIMentor/Mentoraixs/tree/Leroy) 本地跑通后再把 CTA 从 reply yes 切到产品注册链接。

## 环境准备

```bash
git checkout Leroy
pnpm install
cp .env.example .env.local
# 必填：AUTH_SECRET, DATABASE_URL, DATABASE_PROVIDER=pg, DEEPSEEK_API_KEY
# Stripe 测试：STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY, STRIPE_SIGNING_SECRET
pnpm exec tsx scripts/with-env.ts --env .env.local npx drizzle-kit push --config=src/core/db/config.ts
pnpm dev
```

## 测试项

| # | 模块 | 步骤 | 预期 | 结果 | Bug |
|---|------|------|------|------|-----|
| 1 | 注册 | 邮箱+密码注册 | 成功创建账号 | ☐ | |
| 2 | 登录 | 邮箱密码登录 | 进入产品主页 | ☐ | |
| 3 | OTP | 邮箱验证码登录 | 收到码并可登录 | ☐ | |
| 4 | Magic Link | 魔法链接登录 | 邮件链接可登录 | ☐ | |
| 5 | 新用户积分 | 注册后查余额 | 有初始赠送积分 | ☐ | |
| 6 | 每日领积分 | 调用 daily-claim | 积分增加 | ☐ | |
| 7 | Chat | 发一条消息 | 正常回复且扣积分 | ☐ | |
| 8 | Create | 使用一次 Create 工具 | 扣费成功、结果正常 | ☐ | |
| 9 | Stripe 支付 | 测试卡完成一次购买 | 支付成功、积分到账 | ☐ | |
| 10 | 订阅续费 | webhook 模拟（可选） | 积分/权限更新 | ☐ | |
| 11 | 设置页 | Credits / Payments 页 | 余额与流水正确 | ☐ | |
| 12 | 登出再登录 | session 持久 | 数据不丢 | ☐ | |

## Bug 记录模板

| ID | 严重程度 | 模块 | 描述 | 负责人 | 状态 |
|----|----------|------|------|--------|------|
| B1 | P0/P1/P2 | | | 晓宇 | open |

## 通过标准

- 所有 **P0** 项（#1–#9）通过 → 允许在 follow-up 邮件中加入产品注册链接
- Chat 评测（F-3）可并行启动

## 参考文档（Leroy 分支）

- `docs/mvp/auth.md` — 登录体系
- `docs/mvp/credit.md` — 积分体系
- `docs/mvp/stripe-payment-setup.md` — Stripe 配置
