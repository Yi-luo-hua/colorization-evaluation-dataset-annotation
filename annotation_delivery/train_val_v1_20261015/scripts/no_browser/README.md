# 后台浏览器启动拦截器

`batch_auth.py` 只向工作流自有子进程注入本目录的PATH优先级。agy的Windows OAuth打开命令是 `rundll32 url.dll,FileProtocolHandler URL`；本目录同名程序阻止该调用并写入独立标记，不保存URL或认证参数。其他rundll32调用转发给系统程序。不要把本目录加入系统或用户PATH。

新克隆在项目根目录用 Go 构建本地 `rundll32.exe`。Windows GUI 子系统避免额外弹出控制台。

```powershell
go build -trimpath -ldflags='-s -w -H=windowsgui' -o annotation_delivery/train_val_v1_20261015/scripts/no_browser/rundll32.exe annotation_delivery/train_val_v1_20261015/scripts/native/browser_guard.go
```

拦截器缺失时后台调用直接失败，不能退回未保护环境。重新构建会改变运行指纹，须按受控升级流程部署。
