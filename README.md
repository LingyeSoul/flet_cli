# Flet CLI

这是一个修改版的 Flet CLI 0.28.3，主要增加了对 Windows 平台下使用 Nuitka 打包的支持。

原版 Flet CLI 是一个命令行工具，用于构建、运行和打包 Flet 应用。

## 安装

```bash
pip install git+https://github.com/LingyeSoul/flet_cli.git@main
```

此修改版添加了 `packn` 命令，在 Windows 平台上提供更好的 Nuitka 打包支持，可以更有效地将 Flet 应用打包为 Windows 可执行文件。

## 许可证

Apache-2.0