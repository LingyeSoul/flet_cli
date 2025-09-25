# Flet CLI

这是一个修改版的 Flet CLI 0.28.3，主要增加了对 Windows 平台下使用 Nuitka 打包的支持。

原版 Flet CLI 是一个命令行工具，用于构建、运行和打包 Flet 应用。

## 安装

```bash
pip install flet-cli
```

## 使用方法

```bash
# 创建新的 Flet 项目
flet create myapp

# 运行 Flet 应用
flet run

# 构建 Flet 应用
flet build

# 使用 Nuitka 打包 Flet 应用 (Windows 支持)
flet pack

# 打包为 Web 应用
flet packn

# 发布 Flet 应用
flet publish

# 检查 Flet 安装问题
flet doctor
```

## 命令说明

- `create` - 创建新的 Flet 项目
- `run` - 运行 Flet 应用
- `build` - 构建用于分发的 Flet 应用
- `pack` - 将 Flet 应用打包为可执行文件
- `packn` - 将 Flet 应用打包为可执行文件（支持 Windows 下使用 Nuitka）
- `publish` - 发布 Flet 应用到 Flet Gallery
- `doctor` - 检查 Flet 安装中的潜在问题

## Windows 平台 Nuitka 支持

此修改版增强了 `pack` 命令，在 Windows 平台上提供更好的 Nuitka 打包支持，可以更有效地将 Flet 应用打包为 Windows 可执行文件。

## 许可证

Apache-2.0