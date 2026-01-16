# GitHub Actions 自动更新指南

本项目配置了 GitHub Actions 工作流，可以自动检测并更新到 flet-cli 的最新版本。

## 功能特性

- 🔍 **自动检测最新版本** - 从 GitHub API 获取最新的 flet-cli 版本
- 🔄 **自动更新代码** - 下载并整合新版本
- 📦 **保留 packn.py** - 自动将自定义的 packn.py 整合到新版本
- 🚀 **自动提交** - Git 自动提交更改
- 🔀 **可选 PR 创建** - 可选择创建 Pull Request 或直接推送

## 工作流配置

### 位置
`.github/workflows/auto-update.yml`

### 触发方式

#### 1. 手动触发（推荐）
在 GitHub 仓库页面：
1. 进入 **Actions** 标签
2. 选择 **Auto Update flet-cli** 工作流
3. 点击 **Run workflow**
4. 选择是否创建 PR
5. 点击 **Run workflow** 按钮

#### 2. 定时触发（自动）
每天 UTC 时间 9:00 自动运行，检查是否有新版本。

#### 3. API 触发
```bash
# 使用 GitHub CLI
gh workflow run auto-update.yml

# 创建 PR 而不是直接推送
gh workflow run auto-update.yml -f create_pr=true
```

## 工作流程

```
┌─────────────────────────┐
│  触发工作流              │
│  (手动/定时/API)         │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  检测最新 flet-cli 版本  │
│  (GitHub API)           │
└───────────┬─────────────┘
            │
            ▼
      是否有新版本？
           │
    ┌──────┴──────┐
    │             │
   否             是
    │             │
    ▼             ▼
┌────────┐  ┌─────────────────┐
│ 退出   │  │ 下载新版本       │
└────────┘  └────────┬────────┘
                     │
                     ▼
          ┌────────────────────┐
          │ 整合 packn.py      │
          │ 更新配置文件        │
          └────────┬───────────┘
                   │
                   ▼
          ┌────────────────────┐
          │ Git 提交更改       │
          └────────┬───────────┘
                   │
                   ▼
              创建 PR？
                │
         ┌──────┴──────┐
         │             │
        是             否
         │             │
         ▼             ▼
    ┌────────┐    ┌────────┐
    │创建PR  │    │推送主  │
    │并推送  │    │分支    │
    └────────┘    └────────┘
```

## 配置选项

### 环境变量

| 变量 | 说明 | 必需 |
|------|------|------|
| `GITHUB_TOKEN` | GitHub 令牌，用于认证 | 是 |
| `GITHUB_REPOSITORY` | 仓库名称 (owner/repo) | 是 |
| `GITHUB_REF` | Git 引用 | 是 |

### 脚本参数

```bash
python auto_update.py [选项]

选项:
  --create-pr    创建 Pull Request 而不是直接推送到 main
  --auto-merge   自动合并 PR（需要额外权限）
```

## 使用场景

### 场景 1: 测试更新（手动触发，创建 PR）

```bash
# 在本地测试
git checkout -b test-update
python auto_update.py --create-pr

# 或通过 GitHub 界面
# Actions -> Auto Update flet-cli -> Run workflow -> 勾选 "Create Pull Request"
```

### 场景 2: 自动更新（定时触发）

工作流每天自动运行，如果发现新版本：
- 直接推送到 `main` 分支
- 不需要人工干预

### 场景 3: 生产环境（PR 审核流程）

修改工作流配置，默认创建 PR：
```yaml
env:
  CREATE_PR: 'true'
```

## 权限配置

工作流需要以下权限：

```yaml
permissions:
  contents: write      # 读写代码
  pull-requests: write # 创建和合并 PR
```

这些权限已在工作流文件中配置。

## 查看运行日志

### 在 GitHub 上
1. 进入仓库的 **Actions** 标签
2. 选择 **Auto Update flet-cli** 工作流
3. 点击具体的运行记录查看详情

### 日志输出示例

```
============================================================
Flet-Cli Auto Update
============================================================
[*] Fetching latest flet version from GitHub...
    [OK] Latest version: 0.80.2

Current version: 0.80.1
Latest version:  0.80.2
Update required: Yes

[*] Downloading flet-cli 0.80.2...
    URL: https://github.com/flet-dev/flet/archive/refs/tags/0.80.2.tar.gz
    [OK] Downloaded
[*] Extracting archive...
    [OK] Extracted
[*] Integrating packn.py...
    [OK] Copied src
    [OK] Copied LICENSE
    [*] Updating pyproject.toml...
        [OK] Updated
    [*] Updating cli.py...
        [OK] Updated
    [OK] MANIFEST.in exists
    [OK] Integration complete
[*] Committing changes to git...
    [OK] Committed: Update flet-cli to v0.80.2
[*] Pushing to remote...
    [OK] Pushed successfully

============================================================
[SUCCESS] Update completed!
============================================================
```

## 故障排除

### 问题 1: 权限不足

**错误**: `Permission denied (publickey)`

**解决**:
1. 检查仓库设置 -> Actions -> General
2. 确保 **Workflow permissions** 设置为 **Read and write permissions**
3. 保存设置

### 问题 2: GITHUB_TOKEN 未设置

**错误**: `GITHUB_TOKEN not set`

**解决**:
- `GITHUB_TOKEN` 由 GitHub 自动提供，无需手动配置
- 检查工作流文件中是否正确传递了环境变量

### 问题 3: 下载失败

**错误**: `Failed to download flet-cli`

**解决**:
- 检查网络连接
- 确认版本号格式正确（如 `0.80.2`）
- 查看 GitHub API 速率限制

### 问题 4: 无变化导致失败

**错误**: `No changes to commit`

**说明**:
- 这不是错误，说明已经是最新版本
- 工作流会正常退出

## 手动运行脚本

如果需要在本地运行（不使用 GitHub Actions）：

```bash
# 设置 GitHub Token（可选，用于创建 PR）
export GITHUB_TOKEN=your_token_here

# 运行更新
python auto_update.py

# 或创建 PR
python auto_update.py --create-pr
```

## 禁用自动更新

如果要禁用定时自动更新：

1. 编辑 `.github/workflows/auto-update.yml`
2. 注释掉或删除 `schedule` 部分：
   ```yaml
   # schedule:
   #   - cron: '0 9 * * *'
   ```
3. 提交更改

或者完全禁用工作流：
- GitHub 仓库 -> Actions -> Auto Update flet-cli -> Disable workflow

## 最佳实践

### 1. 使用 PR 审核流程
对于重要的生产仓库，建议：
- 默认创建 PR
- 审核通过后再合并
- 测试后再合并到 main

### 2. 监控更新
- 定期检查 Actions 运行日志
- 订阅仓库通知

### 3. 备份
- 在自动化前确保有备份
- 使用 Git 历史可以回滚

### 4. 测试
- 在测试分支上先测试
- 验证 packn 命令正常工作
- 检查构建和安装

## 相关文件

- `auto_update.py` - 自动更新脚本
- `.github/workflows/auto-update.yml` - GitHub Actions 配置
- `integrate_packn.py` - 手动集成工具

## 支持

遇到问题？
1. 查看 [Actions 运行日志](../../actions)
2. 检查 [Issues](../../issues)
3. 提交新的 Issue
