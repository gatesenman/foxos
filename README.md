<p align="center"><img src="assets/icons/icon-256.png" width="128" height="128" alt="狐狸OS 图标"></p>

<h1 align="center">狐狸OS（FoxOS）</h1>

<p align="center">给 AI 智能体使用的桌面操作系统平台：虚拟桌面、应用、文件空间、命令系统和多智能体协作。</p>

## 简介

狐狸OS 是运行在 Windows、macOS 和 Linux 之上的桌面程序。它自带虚拟桌面、应用管理和任务运行时，不依赖 Docker 或虚拟机。多个智能体通过统一的 `foxos` 命令、结构化工具接口和图形界面协作完成办公、设计、研发和业务任务；人可以随时查看、审核和接管。

首个版本聚焦一台 Windows 上的 AI 办公电脑：内置文档、表格和演示应用（来自 [HeyPuter/everything](https://github.com/HeyPuter/everything)），由主管、数据、文档、演示、审核等智能体协作完成任务。

```bash
# 拟设计的命令示例
foxos sheets open sales.xlsx
foxos sheets chart create --type bar --range A1:B12
foxos docs create report.docx
foxos slides chart insert deck.pptx --from sales.xlsx
```

## 主要特性（规划）

- 虚拟桌面、任务中心、智能体中心、应用中心、文件中心、命令终端、活动记录、人工接管
- 每个应用同时提供图形界面、结构化工具接口和 CLI，并有可查询的能力目录
- 多智能体协作：任务拆解、消息、共享文件、写入锁与版本记录
- 权限与审计：工作区隔离、网络与命令权限、敏感操作确认、凭据安全存储
- 在线安装器：各 Everything 应用作为可选组件按需下载
- ACP 客户端：从 ACP Registry 一键安装第三方智能体

## 文档

- [产品规划](docs/product-plan.md)
- [Everything 首批应用代码级评估](docs/everything-evaluation.md)

## 状态

规划与技术验证阶段（阶段 0），尚无可运行代码。

## 资源

- `assets/icon.png`（1024×1024）、`assets/icon.ico`（16–256 多尺寸）
- `assets/icons/icon-{16,24,32,48,64,128,256,512,1024}.png`
- `assets/icon.jpg`（原始图标）

## 许可

本仓库暂未选定许可证。引用的 Everything 应用各有许可（部分为 AGPL-3.0-only），详见评估报告。
