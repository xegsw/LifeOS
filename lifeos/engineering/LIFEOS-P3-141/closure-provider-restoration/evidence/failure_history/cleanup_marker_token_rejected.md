# 清理 marker token 核对

字节检查显示 marker 的既有受控 token 是 lifeos-p3-141-provider-restoration-closure-v1:synthetic-only（附一个终止换行），而非脚本此前假定的较短 token。第三次调用在删除前返回 exit 66；没有删除动作。最后修复将检查收紧为该完整 token，同时仍只允许唯一临时根。
