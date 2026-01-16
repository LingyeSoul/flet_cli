# GitHub Actions 快速参考

## 🚀 快速开始

### 触发更新

```bash
# 方式 1: GitHub 网页界面
1. 打开仓库 -> Actions 标签
2. 选择 "Auto Update flet-cli"
3. 点击 "Run workflow"
4. 选择是否创建 PR
5. 点击 "Run workflow" 按钮

# 方式 2: GitHub CLI
gh workflow run auto-update.yml

# 创建 PR 而不是直接推送
gh workflow run auto-update.yml -f create_pr=true
```

### 本地测试

```bash
# 测试版本检测
python auto_update.py --help

# 模拟更新（不会推送）
python auto_update.py
```

## 📋 工作流程

```
触发 → 检测版本 → 下载源码 → 整合 packn.py → 提交 → 推送/PR
```

## ⚙️ 配置

### 环境变量（自动设置）

- `GITHUB_TOKEN` - GitHub 认证令牌
- `GITHUB_REPOSITORY` - 仓库名称
- `GITHUB_REF` - Git 引用

### 权限（已在 workflow 中配置）

```yaml
permissions:
  contents: write
  pull-requests: write
```

## 📝 输出示例

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
[*] Integrating packn.py...
    [OK] Copied src
    [OK] Integration complete
[*] Committing changes to git...
    [OK] Committed: Update flet-cli to v0.80.2
[*] Pushing to remote...
    [OK] Pushed successfully

============================================================
[SUCCESS] Update completed!
============================================================
```

## 🔄 定时任务

- **默认**: 每天 UTC 9:00 自动运行
- **时区**: UTC
- **检查**: 自动检测并更新到最新版本

## ⚠️ 注意事项

1. **权限**: 确保仓库 Actions 权限设置为 "Read and write"
2. **网络**: 需要能访问 GitHub API
3. **备份**: Git 历史会保留所有更改，可随时回滚
4. **测试**: 建议先在测试分支运行

## 🐛 故障排除

### 查看日志
```
GitHub 仓库 -> Actions -> Auto Update flet-cli -> 点击运行记录
```

### 常见问题

**Q: 权限不足**
- A: 仓库设置 -> Actions -> General -> Workflow permissions -> Read and write

**Q: GITHUB_TOKEN 未设置**
- A: GitHub 自动提供，无需手动配置

**Q: 没有更新**
- A: 可能已经是最新版本，检查日志中的 "No update needed"

## 📚 相关文档

- [完整指南](GITHUB_ACTIONS_GUIDE.md) - 详细配置和使用说明
- [手动集成](INTEGRATION_GUIDE.md) - 使用 integrate_packn.py
- [快速参考](QUICK_START.md) - 命令行快速参考
