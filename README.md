<div align="center">

# 🔨 GitForge-CLI

**Lightweight Terminal Git Workflow Intelligent Enhancement Engine**

**轻量级终端Git工作流智能增强引擎**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-gitstq-black)](https://github.com/gitstq)

[English](#english) | [简体中文](#simplified-chinese) | [繁體中文](#traditional-chinese)

</div>

---

<a name="english"></a>
## English

### Introduction

GitForge-CLI is an intelligent Git workflow enhancement tool that leverages **GLM-5.1 AI** to automatically generate professional commit messages and changelogs. It follows the **Conventional Commits** specification, helping development teams standardize commit practices and streamline release documentation.

**Why GitForge-CLI?**
- **AI-Powered**: Uses GLM-5.1 to analyze git diffs and generate meaningful commit messages
- **Standardized**: Enforces Conventional Commits format (`type(scope): subject`)
- **Multi-language**: Supports English, Simplified Chinese, and Traditional Chinese
- **Zero-dependency core**: Pure Python implementation with minimal dependencies
- **Terminal-native**: Works directly in your terminal, no IDE required

### Core Features

| Feature | Description |
|---------|-------------|
| **AI Commit Generation** | Analyze staged changes and generate professional commit messages |
| **Changelog Automation** | Auto-generate CHANGELOG.md from commit history |
| **Commit Validation** | Validate messages against Conventional Commits spec |
| **Multi-language Support** | EN / ZH / ZH-TW output |
| **Batch Suggestions** | Generate multiple commit message options |
| **Interactive Mode** | Review, edit, and confirm before committing |
| **Repo Analytics** | View repository status and statistics |

### Quick Start

#### Requirements
- Python 3.8+
- Git installed
- GLM API Key (optional, mock mode available)

#### Installation

```bash
# Clone the repository
git clone https://github.com/gitstq/GitForge-CLI.git
cd GitForge-CLI

# Install
pip install -e .

# Or install from source
python setup.py install
```

#### Configuration

```bash
# Set your GLM API key (get one from https://open.bigmodel.cn/)
export GLM_API_KEY="your-api-key"

# Optional: Set custom API base
export GLM_API_BASE="https://open.bigmodel.cn/api/paas/v4"

# Optional: Set model
export GLM_MODEL="glm-5.1"
```

#### Usage

```bash
# Start interactive shell
gitforge

# Generate commit message from staged changes
gitforge commit

# Generate in Chinese
gitforge commit --lang zh

# Generate multiple options
gitforge commit --batch

# Auto-commit without confirmation
gitforge commit --auto

# Generate changelog
gitforge changelog

# Validate a commit message
gitforge validate "feat(auth): add login functionality"

# Show repository status
gitforge status
```

### Detailed Usage Guide

#### Interactive Shell

```bash
$ gitforge

GitForge-CLI v1.0.0
   Lightweight Terminal Git Workflow Intelligent Enhancement Engine

[gitforge]> commit
  Staged files (3):
    src/auth.py
    src/utils.py
    tests/test_auth.py
  Generating commit message...

============================================================
  Generated Commit Message
============================================================

feat(auth): implement JWT-based authentication

- Add login and logout endpoints
- Implement token refresh mechanism
- Add password hashing with bcrypt

Use this message? [Y/n/e(dit)/c(ancel)]:
```

#### Commit Message Validation

```bash
$ gitforge validate "feat: add new feature"

============================================================
  Commit Message Validation
============================================================

Message: feat: add new feature
Valid: Yes
Perfect commit message!
```

#### Changelog Generation

```bash
$ gitforge changelog --version v1.2.0

## [v1.2.0] - 2026-06-06

### Added
- Implement user authentication system
- Add password reset functionality

### Fixed
- Resolve memory leak in session handler
```

### Design Philosophy

GitForge-CLI was designed with these principles:

1. **Developer Experience First**: Minimal setup, intuitive commands
2. **AI-Augmented, Not AI-Dependent**: Works without API key in mock mode
3. **Standards Compliance**: Enforces Conventional Commits specification
4. **Language Inclusive**: Native support for multiple languages
5. **Terminal Native**: No GUI dependencies, works over SSH

### Packaging & Deployment

```bash
# Build distribution
python setup.py sdist bdist_wheel

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Code formatting
black gitforge/ tests/
flake8 gitforge/ tests/
```

### Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<a name="simplified-chinese"></a>
## 简体中文

### 项目介绍

GitForge-CLI 是一款智能 Git 工作流增强工具，利用 **GLM-5.1 AI** 自动生成专业的提交信息和更新日志。它遵循 **Conventional Commits** 规范，帮助开发团队标准化提交实践并简化发布文档工作。

**为什么选择 GitForge-CLI？**
- **AI 驱动**：使用 GLM-5.1 分析 git diff 并生成有意义的提交信息
- **标准化**：强制执行 Conventional Commits 格式 (`type(scope): subject`)
- **多语言支持**：支持英文、简体中文和繁体中文
- **零依赖核心**：纯 Python 实现，依赖极少
- **终端原生**：直接在终端工作，无需 IDE

### 核心特性

| 特性 | 描述 |
|------|------|
| **AI 提交生成** | 分析暂存更改并生成专业的提交信息 |
| **CHANGELOG 自动化** | 基于提交历史自动生成 CHANGELOG.md |
| **提交验证** | 根据 Conventional Commits 规范验证信息 |
| **多语言支持** | 英文 / 简体中文 / 繁體中文 输出 |
| **批量建议** | 生成多个提交信息选项 |
| **交互模式** | 提交前审阅、编辑和确认 |
| **仓库分析** | 查看仓库状态和统计信息 |

### 快速开始

#### 环境要求
- Python 3.8+
- 已安装 Git
- GLM API Key（可选，支持模拟模式）

#### 安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/GitForge-CLI.git
cd GitForge-CLI

# 安装
pip install -e .

# 或从源码安装
python setup.py install
```

#### 配置

```bash
# 设置 GLM API 密钥（从 https://open.bigmodel.cn/ 获取）
export GLM_API_KEY="your-api-key"

# 可选：设置自定义 API 地址
export GLM_API_BASE="https://open.bigmodel.cn/api/paas/v4"

# 可选：设置模型
export GLM_MODEL="glm-5.1"
```

#### 使用

```bash
# 启动交互式 shell
gitforge

# 从暂存更改生成提交信息
gitforge commit

# 生成中文提交信息
gitforge commit --lang zh

# 生成多个选项
gitforge commit --batch

# 自动提交（无需确认）
gitforge commit --auto

# 生成更新日志
gitforge changelog

# 验证提交信息
gitforge validate "feat(auth): 添加登录功能"

# 显示仓库状态
gitforge status
```

### 详细使用指南

#### 交互式 Shell

```bash
$ gitforge

GitForge-CLI v1.0.0
   轻量级终端Git工作流智能增强引擎

[gitforge]> commit
  暂存文件 (3):
    src/auth.py
    src/utils.py
    tests/test_auth.py
  正在生成提交信息...

============================================================
  生成的提交信息
============================================================

feat(auth): 实现基于JWT的身份认证

- 添加登录和登出端点
- 实现令牌刷新机制
- 添加 bcrypt 密码哈希

使用此信息? [Y/n/e(编辑)/c(取消)]:
```

#### 提交信息验证

```bash
$ gitforge validate "feat: 添加新功能"

============================================================
  提交信息验证
============================================================

信息: feat: 添加新功能
有效: 是
完美的提交信息！
```

#### 更新日志生成

```bash
$ gitforge changelog --version v1.2.0

## [v1.2.0] - 2026-06-06

### 新增
- 实现用户认证系统
- 添加密码重置功能

### 修复
- 修复会话处理器的内存泄漏
```

### 设计思路

GitForge-CLI 遵循以下设计原则：

1. **开发者体验优先**：最小化配置，直观的命令
2. **AI 增强而非依赖**：无需 API 密钥也可在模拟模式下工作
3. **标准合规**：强制执行 Conventional Commits 规范
4. **语言包容**：原生支持多种语言
5. **终端原生**：无 GUI 依赖，支持 SSH 环境

### 打包与部署

```bash
# 构建分发包
python setup.py sdist bdist_wheel

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest tests/ -v

# 代码格式化
black gitforge/ tests/
flake8 gitforge/ tests/
```

### 贡献指南

欢迎贡献！请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 了解指南。

### 开源协议

本项目采用 MIT 协议 - 详见 [LICENSE](LICENSE) 文件。

---

<a name="traditional-chinese"></a>
## 繁體中文

### 專案介紹

GitForge-CLI 是一款智慧型 Git 工作流程增強工具，利用 **GLM-5.1 AI** 自動生成專業的提交訊息和更新日誌。它遵循 **Conventional Commits** 規範，幫助開發團隊標準化提交實踐並簡化發布文件工作。

**為什麼選擇 GitForge-CLI？**
- **AI 驅動**：使用 GLM-5.1 分析 git diff 並生成有意義的提交訊息
- **標準化**：強制執行 Conventional Commits 格式 (`type(scope): subject`)
- **多語言支援**：支援英文、簡體中文和繁體中文
- **零依賴核心**：純 Python 實現，依賴極少
- **終端原生**：直接在終端工作，無需 IDE

### 核心特性

| 特性 | 描述 |
|------|------|
| **AI 提交生成** | 分析暫存更改並生成專業的提交訊息 |
| **CHANGELOG 自動化** | 基於提交歷史自動生成 CHANGELOG.md |
| **提交驗證** | 根據 Conventional Commits 規範驗證訊息 |
| **多語言支援** | 英文 / 簡體中文 / 繁體中文 輸出 |
| **批量建議** | 生成多個提交訊息選項 |
| **互動模式** | 提交前審閱、編輯和確認 |
| **倉庫分析** | 查看倉庫狀態和統計資訊 |

### 快速開始

#### 環境要求
- Python 3.8+
- 已安裝 Git
- GLM API Key（可選，支援模擬模式）

#### 安裝

```bash
# 克隆倉庫
git clone https://github.com/gitstq/GitForge-CLI.git
cd GitForge-CLI

# 安裝
pip install -e .

# 或從原始碼安裝
python setup.py install
```

#### 配置

```bash
# 設定 GLM API 金鑰（從 https://open.bigmodel.cn/ 獲取）
export GLM_API_KEY="your-api-key"

# 可選：設定自訂 API 位址
export GLM_API_BASE="https://open.bigmodel.cn/api/paas/v4"

# 可選：設定模型
export GLM_MODEL="glm-5.1"
```

#### 使用

```bash
# 啟動互動式 shell
gitforge

# 從暫存更改生成提交訊息
gitforge commit

# 生成中文提交訊息
gitforge commit --lang zh-tw

# 生成多個選項
gitforge commit --batch

# 自動提交（無需確認）
gitforge commit --auto

# 生成更新日誌
gitforge changelog

# 驗證提交訊息
gitforge validate "feat(auth): 添加登入功能"

# 顯示倉庫狀態
gitforge status
```

### 詳細使用指南

#### 互動式 Shell

```bash
$ gitforge

GitForge-CLI v1.0.0
   輕量級終端Git工作流智能增強引擎

[gitforge]> commit
  暫存檔案 (3):
    src/auth.py
    src/utils.py
    tests/test_auth.py
  正在生成提交訊息...

============================================================
  生成的提交訊息
============================================================

feat(auth): 實現基於JWT的身份認證

- 添加登入和登出端點
- 實現令牌重新整理機制
- 添加 bcrypt 密碼雜湊

使用此訊息? [Y/n/e(編輯)/c(取消)]:
```

#### 提交訊息驗證

```bash
$ gitforge validate "feat: 添加新功能"

============================================================
  提交訊息驗證
============================================================

訊息: feat: 添加新功能
有效: 是
完美的提交訊息！
```

#### 更新日誌生成

```bash
$ gitforge changelog --version v1.2.0

## [v1.2.0] - 2026-06-06

### 新增
- 實現使用者認證系統
- 添加密碼重置功能

### 修復
- 修復會話處理器的記憶體洩漏
```

### 設計理念

GitForge-CLI 遵循以下設計原則：

1. **開發者體驗優先**：最小化配置，直觀的命令
2. **AI 增強而非依賴**：無需 API 金鑰也可在模擬模式下工作
3. **標準合規**：強制執行 Conventional Commits 規範
4. **語言包容**：原生支援多種語言
5. **終端原生**：無 GUI 依賴，支援 SSH 環境

### 打包與部署

```bash
# 構建分發包
python setup.py sdist bdist_wheel

# 安裝開發依賴
pip install -e ".[dev]"

# 執行測試
pytest tests/ -v

# 程式碼格式化
black gitforge/ tests/
flake8 gitforge/ tests/
```

### 貢獻指南

歡迎貢獻！請參閱 [CONTRIBUTING.md](CONTRIBUTING.md) 了解指南。

### 開源協議

本專案採用 MIT 協議 - 詳見 [LICENSE](LICENSE) 文件。
