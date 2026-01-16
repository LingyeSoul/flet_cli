# Flet CLI

这是一个修改版的 Flet CLI，主要增加了对 Windows 平台下使用 Nuitka 打包的支持。

原版 Flet CLI 是一个命令行工具，用于构建、运行和打包 Flet 应用。

## 主要特性

- ✅ 包含所有官方 Flet CLI 功能
- ✅ 新增 `packn` 命令（Windows Nuitka 打包）
- ✅ 自动版本升级工具
- ✅ 与官方版本同步更新

## 安装

### 从 GitHub 安装

```bash
pip install git+https://github.com/LingyeSoul/flet_cli.git@main
```

### 从源码安装

```bash
git clone https://github.com/LingyeSoul/flet_cli.git
cd flet_cli
pip install -e .
```

## 版本升级

本项目提供了两种版本升级方式：

### 方式 1: GitHub Actions 自动更新（推荐）

项目配置了 GitHub Actions 工作流，可以自动检测并更新到最新版本：

**特性：**
- 🔍 自动检测最新版本
- 🔄 自动更新代码
- 📦 保留 packn.py 自定义功能
- 🚀 自动提交更改

**触发方式：**
```bash
# 在 GitHub 仓库页面手动触发
Actions -> Auto Update flet-cli -> Run workflow

# 或使用 GitHub CLI
gh workflow run auto-update.yml
```

详细说明：[GitHub Actions 指南](GITHUB_ACTIONS_GUIDE.md)

### 方式 2: 手动升级

使用 `integrate_packn.py` 脚本手动升级：

```bash
# 升级到指定版本
python integrate_packn.py 0.80.2

# 或使用自动版本检测
python auto_update.py --create-pr
```

### 详细文档

- [GitHub Actions 指南](GITHUB_ACTIONS_GUIDE.md) - 自动化更新配置
- [集成指南](INTEGRATION_GUIDE.md) - 手动版本升级指南
- [快速参考](QUICK_START.md) - 快速命令参考

## packn 命令

此修改版添加了 `packn` 命令，**仅支持 Windows 平台**，使用 Nuitka 打包 Flet 应用：

```bash
flet-cli packn main.py --icon=app.ico --name="MyApp"
```

### 平台要求

**packn 命令系统要求：**
- ✅ Windows 10 或更高版本
- ✅ Python 3.10 或更高版本
- ✅ Nuitka（可选，用于打包）

**注意**: `packn` 命令使用 Nuitka 编译，**目前仅支持 Windows**。

如需 macOS 或 Linux 支持，请使用标准的 `pack` 命令（基于 PyInstaller）。

### 主要参数

- `--icon` - 指定图标文件（.ico, .png, .icns）
- `--name` - 指定生成的可执行文件名称
- `--onefile` / `--onedir` - 打包模式
- `--nuitka-build-args` - 额外的 Nuitka 构建参数

## 开发

### 构建

```bash
python -m build
```

### 测试

```bash
# 本地安装
pip install -e .

# 测试 packn 命令
flet-cli packn --help
```

## 许可证

Apache-2.0（与官方 flet-cli 保持一致）